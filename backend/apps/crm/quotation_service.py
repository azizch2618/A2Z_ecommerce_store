"""CRM quotation draft creation — uses ERP DocumentSequence, no sales orders."""
from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.crm.models import CrmOpportunity
from apps.erp.constants import AuditModule, DocumentType, DomainEventType
from apps.erp.services.audit import AuditService
from apps.erp.services.document_sequence import DocumentSequenceService
from apps.erp.services.events import DomainEventPublisher
from apps.quotes.constants import DEFAULT_QUOTE_TERMS
from apps.trade_accounts.models import Quote


class CrmQuotationService:
    @classmethod
    @transaction.atomic
    def create_draft_from_opportunity(cls, opportunity: CrmOpportunity) -> Quote | None:
        """Create a draft quote when an opportunity is won. Idempotent per opportunity."""
        existing = Quote.objects.filter(
            crm_opportunity=opportunity,
            status=Quote.Status.DRAFT,
        ).first()
        if existing:
            return existing

        quote_number = DocumentSequenceService.next_number(DocumentType.QUOTE)
        valid_until = timezone.now() + timedelta(days=30)

        quote = Quote.objects.create(
            trade_account=opportunity.trade_account,
            crm_opportunity=opportunity,
            party=opportunity.party,
            customer=opportunity.customer,
            quote_number=quote_number,
            status=Quote.Status.DRAFT,
            valid_until=valid_until,
            total_inc_gst_cents=opportunity.expected_revenue_cents,
            terms_and_conditions=DEFAULT_QUOTE_TERMS,
        )

        DomainEventPublisher.publish(
            event_type=DomainEventType.QUOTE_CREATED,
            aggregate_type="quote",
            aggregate_id=str(quote.public_id),
            payload={
                "quote_number": quote.quote_number,
                "opportunity_id": str(opportunity.public_id),
                "party_id": str(opportunity.party.public_id) if opportunity.party else None,
                "source": "crm_opportunity_won",
            },
            idempotency_key=f"quote.created:crm:{opportunity.public_id}",
        )

        AuditService.log(
            user=None,
            module=AuditModule.QUOTES,
            action="quote_draft_created",
            resource_type="quote",
            resource_id=str(quote.public_id),
            summary=f"Quotation draft {quote.quote_number} created from opportunity {opportunity.name}",
            metadata={"opportunity_id": str(opportunity.public_id)},
            mirror_operational=False,
        )
        return quote
