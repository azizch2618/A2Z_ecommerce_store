"""Register receivables accounting handlers."""
from apps.accounting.services import AccountingEventProcessor
from apps.erp.constants import DomainEventType
from apps.erp.models import DomainEvent
from apps.erp.services.events import _register_handler


@_register_handler(DomainEventType.AR_INVOICE_ISSUED)
@_register_handler(DomainEventType.AR_PAYMENT_RECEIVED)
@_register_handler(DomainEventType.AR_CREDIT_NOTE_ISSUED)
def _receivables_accounting_handler(event: DomainEvent) -> None:
    AccountingEventProcessor.process_event(
        event_type=event.event_type,
        payload=event.payload or {},
        aggregate_id=event.aggregate_id,
    )
