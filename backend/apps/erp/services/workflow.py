"""Generic approval workflow engine."""
from __future__ import annotations

from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.accounts.services import RoleService
from apps.core.exceptions import BusinessRuleError, NotFoundError
from apps.erp.constants import DomainEventType, WorkflowInstanceStatus
from apps.erp.models import WorkflowAction, WorkflowDefinition, WorkflowInstance
from apps.erp.services.events import DomainEventPublisher


class WorkflowEngine:
    @staticmethod
    def get_definition(code: str) -> WorkflowDefinition:
        from apps.erp.bootstrap import ensure_foundation

        ensure_foundation()
        try:
            return WorkflowDefinition.objects.get(code=code, is_active=True)
        except WorkflowDefinition.DoesNotExist as exc:
            raise NotFoundError(f"Workflow definition '{code}' not found.") from exc

    @classmethod
    @transaction.atomic
    def start(
        cls,
        *,
        definition_code: str,
        resource_type: str,
        resource_id: str,
        actor=None,
        assigned_to=None,
        metadata: dict[str, Any] | None = None,
    ) -> WorkflowInstance:
        definition = cls.get_definition(definition_code)
        instance = WorkflowInstance.objects.create(
            definition=definition,
            current_state=definition.initial_state,
            resource_type=resource_type,
            resource_id=str(resource_id),
            assigned_to=assigned_to,
            status=WorkflowInstanceStatus.ACTIVE,
            history=[
                {
                    "state": definition.initial_state,
                    "action": "start",
                    "actor_id": str(getattr(actor, "public_id", "")) if actor else None,
                    "at": timezone.now().isoformat(),
                }
            ],
            metadata=metadata or {},
        )
        return instance

    @classmethod
    @transaction.atomic
    def transition(
        cls,
        *,
        instance: WorkflowInstance,
        action: str,
        actor,
        comment: str = "",
        required_roles: list[str] | None = None,
    ) -> WorkflowInstance:
        if instance.status != WorkflowInstanceStatus.ACTIVE:
            raise BusinessRuleError("Workflow instance is not active.")

        definition = instance.definition
        transition = cls._find_transition(definition, instance.current_state, action)
        if transition is None:
            raise BusinessRuleError(
                f"Action '{action}' is not allowed from state '{instance.current_state}'."
            )

        roles = required_roles or transition.get("required_roles", [])
        if roles and actor:
            if not any(RoleService.has_role(actor, role) for role in roles):
                raise BusinessRuleError("Insufficient role for this workflow action.")

        from_state = instance.current_state
        to_state = transition["to"]

        WorkflowAction.objects.create(
            instance=instance,
            action=action,
            actor=actor if getattr(actor, "is_authenticated", False) else None,
            from_state=from_state,
            to_state=to_state,
            comment=comment,
        )

        history_entry = {
            "state": to_state,
            "action": action,
            "from_state": from_state,
            "actor_id": str(getattr(actor, "public_id", "")) if actor else None,
            "comment": comment,
            "at": timezone.now().isoformat(),
        }
        instance.history = [*instance.history, history_entry]
        instance.current_state = to_state

        if to_state in transition.get("terminal_states", []) or to_state in (
            "approved",
            "rejected",
            "cancelled",
            "completed",
        ):
            instance.status = WorkflowInstanceStatus.COMPLETED
            instance.completed_at = timezone.now()
            DomainEventPublisher.publish(
                event_type=DomainEventType.WORKFLOW_COMPLETED,
                aggregate_type=instance.resource_type,
                aggregate_id=instance.resource_id,
                payload={
                    "workflow_code": definition.code,
                    "final_state": to_state,
                    "action": action,
                },
            )

        instance.save(
            update_fields=[
                "current_state",
                "history",
                "status",
                "completed_at",
                "updated_at",
            ],
        )
        return instance

    @staticmethod
    def _find_transition(
        definition: WorkflowDefinition,
        from_state: str,
        action: str,
    ) -> dict | None:
        for transition in definition.transitions:
            if transition.get("from") == from_state and transition.get("action") == action:
                return transition
        return None

    @staticmethod
    def get_for_resource(*, resource_type: str, resource_id: str) -> WorkflowInstance | None:
        return (
            WorkflowInstance.objects.filter(
                resource_type=resource_type,
                resource_id=str(resource_id),
                status=WorkflowInstanceStatus.ACTIVE,
            )
            .order_by("-created_at")
            .first()
        )

    @staticmethod
    def available_actions(instance: WorkflowInstance) -> list[dict]:
        return [
            t
            for t in instance.definition.transitions
            if t.get("from") == instance.current_state
        ]
