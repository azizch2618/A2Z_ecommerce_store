"""Domain event outbox publisher."""
from __future__ import annotations

import uuid
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.erp.constants import DomainEventStatus, DomainEventType
from apps.erp.models import DomainEvent


class DomainEventPublisher:
    @staticmethod
    @transaction.atomic
    def publish(
        *,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        payload: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        auto_dispatch: bool = True,
    ) -> DomainEvent:
        key = idempotency_key or f"{event_type}:{aggregate_type}:{aggregate_id}:{uuid.uuid4().hex[:12]}"
        existing = DomainEvent.objects.filter(idempotency_key=key).first()
        if existing:
            return existing

        event = DomainEvent.objects.create(
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=str(aggregate_id),
            payload=payload or {},
            idempotency_key=key,
            status=DomainEventStatus.PENDING,
            occurred_at=timezone.now(),
        )

        if auto_dispatch:
            DomainEventPublisher.dispatch(event)

        return event

    @staticmethod
    def dispatch(event: DomainEvent) -> None:
        """Process a pending event (in-process handlers; Celery hook for future)."""
        handlers = _EVENT_HANDLERS.get(event.event_type, [])
        try:
            for handler in handlers:
                handler(event)
            event.status = DomainEventStatus.PUBLISHED
            event.published_at = timezone.now()
            event.error_message = ""
            event.save(update_fields=["status", "published_at", "error_message", "updated_at"])
        except Exception as exc:  # noqa: BLE001 — outbox must record handler failures
            event.status = DomainEventStatus.FAILED
            event.error_message = str(exc)[:2000]
            event.save(update_fields=["status", "error_message", "updated_at"])
            raise

    @staticmethod
    def replay_pending(*, limit: int = 100) -> int:
        pending = DomainEvent.objects.filter(status=DomainEventStatus.PENDING).order_by(
            "occurred_at"
        )[:limit]
        count = 0
        for event in pending:
            DomainEventPublisher.dispatch(event)
            count += 1
        return count


def _register_handler(event_type: str):
    def decorator(fn):
        _EVENT_HANDLERS.setdefault(event_type, []).append(fn)
        return fn

    return decorator


_EVENT_HANDLERS: dict[str, list] = {}


@_register_handler(DomainEventType.ORDER_CREATED)
@_register_handler(DomainEventType.ORDER_PAID)
@_register_handler(DomainEventType.TRADE_APPROVED)
@_register_handler(DomainEventType.PO_RECEIVED)
@_register_handler(DomainEventType.INVENTORY_RECEIVED)
def _audit_event_handler(event: DomainEvent) -> None:
    from apps.erp.services.audit import AuditService

    AuditService.log(
        user=None,
        module=event.aggregate_type,
        action=event.event_type,
        resource_type=event.aggregate_type,
        resource_id=event.aggregate_id,
        summary=f"Domain event {event.event_type}",
        metadata=event.payload,
        mirror_operational=False,
    )
