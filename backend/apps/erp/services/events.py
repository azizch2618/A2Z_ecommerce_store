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


@_register_handler(DomainEventType.CRM_OPPORTUNITY_WON)
def _crm_opportunity_won_handler(event: DomainEvent) -> None:
    from apps.crm.models import CrmOpportunity
    from apps.crm.quotation_service import CrmQuotationService

    opportunity = (
        CrmOpportunity.objects.filter(public_id=event.aggregate_id)
        .select_related("party", "customer", "trade_account")
        .first()
    )
    if opportunity is None:
        return
    CrmQuotationService.create_draft_from_opportunity(opportunity)


@_register_handler(DomainEventType.QUOTE_DRAFT_CREATED)
def _quote_draft_created_handler(event: DomainEvent) -> None:
    from apps.erp.constants import AuditModule
    from apps.erp.services.audit import AuditService

    AuditService.log(
        user=None,
        module=AuditModule.QUOTES,
        action=event.event_type,
        resource_type=event.aggregate_type,
        resource_id=event.aggregate_id,
        summary=f"Quote draft created: {event.payload.get('quote_number', '')}",
        metadata=event.payload,
        mirror_operational=False,
    )


@_register_handler(DomainEventType.QUOTE_CREATED)
def _quote_created_handler(event: DomainEvent) -> None:
    from apps.erp.constants import AuditModule
    from apps.erp.services.audit import AuditService

    AuditService.log(
        user=None,
        module=AuditModule.QUOTES,
        action=event.event_type,
        resource_type=event.aggregate_type,
        resource_id=event.aggregate_id,
        summary=f"Quote created: {event.payload.get('quote_number', '')}",
        metadata=event.payload,
        mirror_operational=False,
    )


@_register_handler(DomainEventType.QUOTE_APPROVED)
def _quote_approved_handler(event: DomainEvent) -> None:
    from apps.erp.constants import AuditModule
    from apps.erp.services.audit import AuditService

    AuditService.log(
        user=None,
        module=AuditModule.QUOTES,
        action=event.event_type,
        resource_type=event.aggregate_type,
        resource_id=event.aggregate_id,
        summary=f"Quote approved: {event.payload.get('quote_number', '')}",
        metadata=event.payload,
        mirror_operational=False,
    )


@_register_handler(DomainEventType.QUOTE_ACCEPTED)
def _quote_accepted_handler(event: DomainEvent) -> None:
    from apps.erp.constants import AuditModule
    from apps.erp.services.audit import AuditService
    from apps.erp.services.notifications import NotificationService
    from apps.trade_accounts.models import Quote

    quote = Quote.objects.filter(public_id=event.aggregate_id).select_related("created_by").first()
    if quote and quote.created_by:
        NotificationService.send(
            recipient=quote.created_by,
            channel="in_app",
            subject=f"Quote {quote.quote_number} accepted",
            body="The customer has accepted your quotation.",
            resource_type="quote",
            resource_id=str(quote.public_id),
        )

    AuditService.log(
        user=None,
        module=AuditModule.QUOTES,
        action=event.event_type,
        resource_type=event.aggregate_type,
        resource_id=event.aggregate_id,
        summary=f"Quote accepted: {event.payload.get('quote_number', '')}",
        metadata=event.payload,
        mirror_operational=False,
    )


@_register_handler(DomainEventType.QUOTE_CONVERTED)
def _quote_converted_handler(event: DomainEvent) -> None:
    from apps.erp.constants import AuditModule
    from apps.erp.services.audit import AuditService

    AuditService.log(
        user=None,
        module=AuditModule.QUOTES,
        action=event.event_type,
        resource_type=event.aggregate_type,
        resource_id=event.aggregate_id,
        summary=f"Quote converted to order {event.payload.get('order_number', '')}",
        metadata=event.payload,
        mirror_operational=False,
    )
