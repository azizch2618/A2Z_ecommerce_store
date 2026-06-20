"""Quotation business logic — workflow, conversion, totals."""
from __future__ import annotations

from datetime import timedelta
from typing import Any
from uuid import UUID

from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q, QuerySet
from django.utils import timezone

from apps.catalog.models import ProductVariant
from apps.core.exceptions import BusinessRuleError, NotFoundError
from apps.customers.models import Customer
from apps.erp.constants import AuditModule, DocumentType, DomainEventType, WorkflowCode
from apps.erp.services.audit import AuditService
from apps.erp.services.document_sequence import DocumentSequenceService
from apps.erp.services.events import DomainEventPublisher
from apps.erp.services.notifications import NotificationService
from apps.erp.services.party import PartyService
from apps.erp.services.workflow import WorkflowEngine
from apps.orders.models import Order, OrderItem
from apps.orders.services import OrderService
from apps.pricing.services import PricingService
from apps.quotes.constants import DEFAULT_QUOTE_TERMS, quote_approval_threshold_cents
from apps.trade_accounts.models import Quote, QuoteLine


class QuoteService:
    @staticmethod
    def list_quotes(
        *,
        status: str | None = None,
        customer_id: UUID | None = None,
        search: str | None = None,
    ) -> QuerySet[Quote]:
        qs = Quote.objects.select_related(
            "customer", "party", "trade_account", "crm_opportunity", "created_by"
        ).prefetch_related("lines")
        if status:
            qs = qs.filter(status=status)
        if customer_id:
            qs = qs.filter(customer__public_id=customer_id)
        if search:
            qs = qs.filter(
                Q(quote_number__icontains=search)
                | Q(party__display_name__icontains=search)
                | Q(notes__icontains=search)
            )
        return qs.order_by("-created_at")

    @staticmethod
    def get_quote(public_id: UUID) -> Quote:
        quote = (
            QuoteService.list_quotes()
            .filter(public_id=public_id)
            .first()
        )
        if not quote:
            raise NotFoundError("Quote not found.")
        return quote

    @classmethod
    @transaction.atomic
    def create_quote(cls, *, actor, data: dict[str, Any]) -> Quote:
        customer = cls._resolve_customer(data.get("customer_id"))
        party = cls._resolve_party(data.get("party_id"), customer)
        trade_account = cls._resolve_trade_account(data.get("trade_account_id"), customer)

        quote_number = data.get("quote_number") or DocumentSequenceService.next_number(
            DocumentType.QUOTE
        )
        valid_until = data.get("valid_until") or (timezone.now() + timedelta(days=30))

        quote = Quote.objects.create(
            quote_number=quote_number,
            customer=customer,
            party=party,
            trade_account=trade_account,
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
            valid_until=valid_until,
            notes=data.get("notes", ""),
            terms_and_conditions=data.get("terms_and_conditions") or DEFAULT_QUOTE_TERMS,
            status=Quote.Status.DRAFT,
        )
        if data.get("crm_opportunity_id"):
            from apps.crm.models import CrmOpportunity

            opp = CrmOpportunity.objects.filter(public_id=data["crm_opportunity_id"]).first()
            if opp:
                quote.crm_opportunity = opp
                quote.save(update_fields=["crm_opportunity", "updated_at"])

        cls._audit(actor, quote, "create", "Quote created")
        DomainEventPublisher.publish(
            event_type=DomainEventType.QUOTE_CREATED,
            aggregate_type="quote",
            aggregate_id=str(quote.public_id),
            payload={"quote_number": quote.quote_number, "status": quote.status},
            idempotency_key=f"quote.created:{quote.public_id}",
        )
        return quote

    @classmethod
    @transaction.atomic
    def update_quote(cls, *, quote: Quote, actor, data: dict[str, Any]) -> Quote:
        if quote.status not in (Quote.Status.DRAFT, Quote.Status.REJECTED):
            raise BusinessRuleError("Only draft or rejected quotes can be edited.")
        for field in ("notes", "terms_and_conditions", "valid_until", "discount_cents"):
            if field in data:
                setattr(quote, field, data[field])
        quote.save()
        cls._audit(actor, quote, "update", "Quote updated")
        return quote

    @classmethod
    @transaction.atomic
    def add_line(cls, *, quote: Quote, actor, data: dict[str, Any]) -> QuoteLine:
        if quote.status not in (Quote.Status.DRAFT, Quote.Status.REJECTED):
            raise BusinessRuleError("Cannot add lines to this quote.")
        variant = ProductVariant.objects.select_related("product").filter(
            public_id=data["variant_id"]
        ).first()
        if not variant:
            raise NotFoundError("Product variant not found.")
        qty = int(data.get("quantity", 1))
        unit_ex = int(data.get("unit_price_ex_gst_cents", 0))
        if unit_ex <= 0:
            from apps.catalog.pricing_helpers import get_variant_unit_price_cents

            unit_ex = get_variant_unit_price_cents(variant)
        discount = int(data.get("discount_cents", 0))
        line_ex = max(unit_ex * qty - discount, 0)
        line_gst = PricingService.calculate_gst(line_ex)
        line = QuoteLine.objects.create(
            quote=quote,
            variant=variant,
            sku=variant.sku,
            product_name=variant.product.name,
            quantity=qty,
            unit_price_ex_gst_cents=unit_ex,
            discount_cents=discount,
            line_subtotal_ex_gst_cents=line_ex,
            line_gst_cents=line_gst,
            line_total_inc_gst_cents=line_ex + line_gst,
            gst_rate=PricingService.GST_RATE,
        )
        cls.recalculate_totals(quote)
        cls._audit(actor, quote, "add_line", f"Line added: {line.sku}")
        return line

    @staticmethod
    def recalculate_totals(quote: Quote) -> Quote:
        lines = quote.lines.all()
        subtotal_ex = sum(line.line_subtotal_ex_gst_cents for line in lines)
        gst_total = sum(line.line_gst_cents for line in lines)
        discount = quote.discount_cents or 0
        total_inc = max(subtotal_ex + gst_total - discount, 0)
        quote.subtotal_ex_gst_cents = subtotal_ex
        quote.gst_total_cents = gst_total
        quote.total_inc_gst_cents = total_inc
        quote.save(
            update_fields=[
                "subtotal_ex_gst_cents",
                "gst_total_cents",
                "total_inc_gst_cents",
                "updated_at",
            ]
        )
        return quote

    @classmethod
    @transaction.atomic
    def submit_for_approval(cls, *, quote: Quote, actor) -> Quote:
        if quote.status != Quote.Status.DRAFT:
            raise BusinessRuleError("Only draft quotes can be submitted.")
        if not quote.lines.exists() and quote.total_inc_gst_cents <= 0:
            raise BusinessRuleError("Quote must have line items or a total before submission.")

        threshold = quote_approval_threshold_cents()
        if quote.total_inc_gst_cents >= threshold:
            quote.status = Quote.Status.PENDING_APPROVAL
            WorkflowEngine.start(
                definition_code=WorkflowCode.QUOTE_APPROVAL,
                resource_type="quote",
                resource_id=str(quote.public_id),
                actor=actor,
            )
            if quote.created_by:
                NotificationService.send(
                    recipient=quote.created_by,
                    channel="in_app",
                    subject=f"Quote {quote.quote_number} pending approval",
                    body=f"Quote total {quote.total_inc_gst_cents / 100:.2f} AUD requires manager approval.",
                    resource_type="quote",
                    resource_id=str(quote.public_id),
                )
        else:
            quote.status = Quote.Status.APPROVED
        quote.save(update_fields=["status", "updated_at"])
        cls._audit(actor, quote, "submit", "Quote submitted")
        return quote

    @classmethod
    @transaction.atomic
    def approve(cls, *, quote: Quote, actor, comment: str = "") -> Quote:
        if quote.status != Quote.Status.PENDING_APPROVAL:
            raise BusinessRuleError("Quote is not pending approval.")
        instance = WorkflowEngine.get_for_resource(
            resource_type="quote", resource_id=str(quote.public_id)
        )
        if instance:
            WorkflowEngine.transition(
                instance=instance, action="approve", actor=actor, comment=comment
            )
        quote.status = Quote.Status.APPROVED
        quote.save(update_fields=["status", "updated_at"])
        cls._audit(actor, quote, "approve", comment or "Quote approved")
        DomainEventPublisher.publish(
            event_type=DomainEventType.QUOTE_APPROVED,
            aggregate_type="quote",
            aggregate_id=str(quote.public_id),
            payload={"quote_number": quote.quote_number},
            idempotency_key=f"quote.approved:{quote.public_id}",
        )
        return quote

    @classmethod
    @transaction.atomic
    def reject(cls, *, quote: Quote, actor, comment: str = "") -> Quote:
        if quote.status != Quote.Status.PENDING_APPROVAL:
            raise BusinessRuleError("Quote is not pending approval.")
        instance = WorkflowEngine.get_for_resource(
            resource_type="quote", resource_id=str(quote.public_id)
        )
        if instance:
            WorkflowEngine.transition(
                instance=instance, action="reject", actor=actor, comment=comment
            )
        quote.status = Quote.Status.REJECTED
        quote.rejected_at = timezone.now()
        quote.save(update_fields=["status", "rejected_at", "updated_at"])
        cls._audit(actor, quote, "reject", comment or "Quote rejected")
        return quote

    @classmethod
    @transaction.atomic
    def send_to_customer(cls, *, quote: Quote, actor) -> Quote:
        if quote.status == Quote.Status.DRAFT:
            if quote.total_inc_gst_cents >= quote_approval_threshold_cents():
                raise BusinessRuleError("Quote requires approval before sending.")
            quote.status = Quote.Status.APPROVED
        elif quote.status != Quote.Status.APPROVED:
            raise BusinessRuleError("Quote must be approved before sending.")
        quote.status = Quote.Status.SENT
        quote.sent_at = timezone.now()
        quote.save(update_fields=["status", "sent_at", "updated_at"])
        cls._audit(actor, quote, "send", "Quote sent to customer")
        return quote

    @classmethod
    @transaction.atomic
    def customer_accept(cls, *, quote: Quote, customer: Customer) -> Quote:
        if quote.status != Quote.Status.SENT:
            raise BusinessRuleError("Quote is not available for acceptance.")
        if quote.customer_id and quote.customer_id != customer.id:
            raise BusinessRuleError("You cannot accept this quote.")
        if quote.valid_until < timezone.now():
            quote.status = Quote.Status.EXPIRED
            quote.save(update_fields=["status", "updated_at"])
            raise BusinessRuleError("Quote has expired.")
        quote.status = Quote.Status.ACCEPTED
        quote.accepted_at = timezone.now()
        quote.save(update_fields=["status", "accepted_at", "updated_at"])
        cls._audit(None, quote, "accept", "Quote accepted by customer")
        DomainEventPublisher.publish(
            event_type=DomainEventType.QUOTE_ACCEPTED,
            aggregate_type="quote",
            aggregate_id=str(quote.public_id),
            payload={"quote_number": quote.quote_number, "customer_id": str(customer.public_id)},
            idempotency_key=f"quote.accepted:{quote.public_id}",
        )
        return quote

    @classmethod
    @transaction.atomic
    def customer_reject(cls, *, quote: Quote, customer: Customer, reason: str = "") -> Quote:
        if quote.status != Quote.Status.SENT:
            raise BusinessRuleError("Quote is not available for rejection.")
        if quote.customer_id and quote.customer_id != customer.id:
            raise BusinessRuleError("You cannot reject this quote.")
        quote.status = Quote.Status.REJECTED
        quote.rejected_at = timezone.now()
        quote.metadata = {**quote.metadata, "customer_reject_reason": reason}
        quote.save(update_fields=["status", "rejected_at", "metadata", "updated_at"])
        cls._audit(None, quote, "customer_reject", reason or "Rejected by customer")
        return quote

    @classmethod
    @transaction.atomic
    def convert_to_order(cls, *, quote: Quote, actor) -> Order:
        if quote.status != Quote.Status.ACCEPTED:
            raise BusinessRuleError("Only accepted quotes can be converted to orders.")
        if quote.converted_order_id:
            return quote.converted_order
        if not quote.customer:
            raise BusinessRuleError("Quote must be linked to a customer to convert.")
        if not quote.lines.exists():
            raise BusinessRuleError("Quote must have line items to convert.")

        customer = quote.customer
        order = Order.objects.create(
            order_number=OrderService.generate_order_number(),
            customer=customer,
            organization=customer.organization,
            trade_account=quote.trade_account,
            status=Order.Status.PENDING,
            payment_status=Order.PaymentStatus.PENDING,
            currency_code=quote.currency_code,
            subtotal_ex_gst_cents=quote.subtotal_ex_gst_cents,
            gst_total_cents=quote.gst_total_cents,
            discount_cents=quote.discount_cents,
            total_inc_gst_cents=quote.total_inc_gst_cents,
            placed_at=timezone.now(),
            customer_notes=quote.notes,
            billing_address={"line1": "", "suburb": "", "state": "", "postcode": "", "country": "AU"},
            shipping_address={"line1": "", "suburb": "", "state": "", "postcode": "", "country": "AU"},
        )
        for line in quote.lines.select_related("variant", "variant__product"):
            OrderItem.objects.create(
                order=order,
                variant=line.variant,
                sku=line.sku,
                product_name=line.product_name,
                variant_name=line.variant.name,
                quantity=line.quantity,
                unit_price_ex_gst_cents=line.unit_price_ex_gst_cents,
                unit_gst_cents=PricingService.calculate_gst(line.unit_price_ex_gst_cents),
                gst_rate=line.gst_rate,
                line_total_ex_gst_cents=line.line_subtotal_ex_gst_cents,
                line_gst_cents=line.line_gst_cents,
                line_total_inc_gst_cents=line.line_total_inc_gst_cents,
            )

        quote.status = Quote.Status.CONVERTED
        quote.converted_order = order
        quote.save(update_fields=["status", "converted_order", "updated_at"])

        cls._audit(actor, quote, "convert", f"Converted to order {order.order_number}")
        DomainEventPublisher.publish(
            event_type=DomainEventType.QUOTE_CONVERTED,
            aggregate_type="quote",
            aggregate_id=str(quote.public_id),
            payload={
                "quote_number": quote.quote_number,
                "order_number": order.order_number,
                "order_id": str(order.public_id),
            },
            idempotency_key=f"quote.converted:{quote.public_id}",
        )
        DomainEventPublisher.publish(
            event_type=DomainEventType.ORDER_CREATED,
            aggregate_type="order",
            aggregate_id=str(order.public_id),
            payload={"order_number": order.order_number, "from_quote": quote.quote_number},
            idempotency_key=f"order.from_quote:{quote.public_id}",
        )
        return order

    @staticmethod
    def get_dashboard_kpis() -> dict[str, Any]:
        qs = Quote.objects.all()
        draft = qs.filter(status=Quote.Status.DRAFT).count()
        pending = qs.filter(status=Quote.Status.PENDING_APPROVAL).count()
        accepted = qs.filter(status=Quote.Status.ACCEPTED).count()
        converted = qs.filter(status=Quote.Status.CONVERTED).count()
        sent = qs.filter(status=Quote.Status.SENT).count()
        conversion_rate = round((converted / sent) * 100, 1) if sent else 0.0
        return {
            "draft_quotes": draft,
            "pending_approval": pending,
            "accepted": accepted,
            "converted": converted,
            "conversion_rate": conversion_rate,
        }

    @staticmethod
    def _resolve_customer(customer_id) -> Customer | None:
        if not customer_id:
            return None
        customer = Customer.objects.filter(public_id=customer_id).first()
        if not customer:
            raise NotFoundError("Customer not found.")
        PartyService.ensure_for_customer(customer)
        return customer

    @staticmethod
    def _resolve_party(party_id, customer: Customer | None):
        if party_id:
            from apps.erp.models import Party

            party = Party.objects.filter(public_id=party_id).first()
            if party:
                return party
        if customer:
            return PartyService.ensure_for_customer(customer)
        return None

    @staticmethod
    def _resolve_trade_account(trade_account_id, customer: Customer | None):
        if trade_account_id:
            from apps.trade_accounts.models import TradeAccount

            account = TradeAccount.objects.filter(public_id=trade_account_id).first()
            if account:
                return account
        if customer and customer.organization_id:
            from apps.trade_accounts.models import TradeAccount

            return TradeAccount.objects.filter(organization=customer.organization).first()
        return None

    @staticmethod
    def _audit(user, quote: Quote, action: str, summary: str) -> None:
        AuditService.log(
            user=user,
            module=AuditModule.QUOTES,
            action=action,
            resource_type="quote",
            resource_id=str(quote.public_id),
            summary=summary,
            metadata={"quote_number": quote.quote_number, "status": quote.status},
            mirror_operational=False,
        )
