"""Register accounting handlers on domain events."""
from __future__ import annotations

from apps.accounting.services import AccountingEventProcessor
from apps.erp.constants import DomainEventType
from apps.erp.models import DomainEvent
from apps.erp.services.events import _register_handler


@_register_handler(DomainEventType.ORDER_PAID)
@_register_handler(DomainEventType.GOODS_RECEIVED)
@_register_handler(DomainEventType.INVENTORY_ADJUSTED)
@_register_handler(DomainEventType.TRADE_APPROVED)
def _accounting_event_handler(event: DomainEvent) -> None:
    AccountingEventProcessor.process_event(
        event_type=event.event_type,
        payload=event.payload or {},
        aggregate_id=event.aggregate_id,
    )
