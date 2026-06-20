"""Accounts Receivable business logic."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import Q, QuerySet, Sum
from django.utils import timezone

from apps.accounting.audit import AccountingAuditService
from apps.accounting.services import AccountingEventProcessor
from apps.accounting.tax import TaxEngine
from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.customers.models import Customer
from apps.erp.constants import AuditModule, DocumentType, DomainEventType, WorkflowCode
from apps.erp.services.audit import AuditService
from apps.erp.services.document_sequence import DocumentSequenceService
from apps.erp.services.events import DomainEventPublisher
from apps.erp.services.notifications import NotificationService
from apps.erp.services.party import PartyService
from apps.erp.services.workflow import WorkflowEngine
from apps.orders.models import Order
from apps.receivables.constants import CreditNoteStatus, CustomerInvoiceStatus, PaymentMethod
from apps.receivables.models import (
    CreditNote,
    CustomerInvoice,
    CustomerInvoiceLine,
    CustomerPayment,
    CustomerPaymentAllocation,
)


def _next_invoice_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.INVOICE)


def _next_payment_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.AR_PAYMENT)


def _next_credit_note_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.CREDIT_NOTE)


class CustomerInvoiceService:
    @staticmethod
    def list_invoices(
        *,
        status: str | None = None,
        customer_id: UUID | None = None,
    ) -> QuerySet[CustomerInvoice]:
        qs = CustomerInvoice.objects.select_related(
            "customer", "customer__user", "order", "issued_by"
        ).prefetch_related("lines")
        if status:
            qs = qs.filter(status=status)
        if customer_id:
            qs = qs.filter(customer__public_id=customer_id)
        return qs.order_by("-created_at")

    @staticmethod
    def get_invoice(public_id: UUID) -> CustomerInvoice:
        inv = CustomerInvoiceService.list_invoices().filter(public_id=public_id).first()
        if not inv:
            raise NotFoundError("Customer invoice not found.")
        return inv

    @classmethod
    def _recalculate_totals(cls, invoice: CustomerInvoice) -> None:
        lines = invoice.lines.all()
        subtotal = sum(line.line_ex_gst_cents for line in lines)
        gst = sum(line.line_gst_cents for line in lines)
        total = subtotal + gst
        balance = total - invoice.amount_paid_cents
        invoice.subtotal_ex_gst_cents = subtotal
        invoice.gst_cents = gst
        invoice.total_inc_gst_cents = total
        invoice.balance_due_cents = max(0, balance)
        invoice.save(
            update_fields=[
                "subtotal_ex_gst_cents",
                "gst_cents",
                "total_inc_gst_cents",
                "balance_due_cents",
                "updated_at",
            ]
        )

    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        customer: Customer,
        actor,
        order: Order | None = None,
        payment_terms_days: int | None = None,
        notes: str = "",
    ) -> CustomerInvoice:
        terms = payment_terms_days or customer.payment_terms_days or 30
        invoice = CustomerInvoice.objects.create(
            invoice_number=_next_invoice_number(),
            customer=customer,
            order=order,
            payment_terms_days=terms,
            notes=notes,
            status=CustomerInvoiceStatus.DRAFT,
        )
        PartyService.ensure_for_customer(customer)
        cls._audit(actor, invoice, "create", f"Draft invoice {invoice.invoice_number} created")
        return invoice

    @classmethod
    @transaction.atomic
    def create_from_order(cls, *, order: Order, actor) -> CustomerInvoice:
        existing = CustomerInvoice.objects.filter(
            order=order,
            status__in=[
                CustomerInvoiceStatus.DRAFT,
                CustomerInvoiceStatus.ISSUED,
                CustomerInvoiceStatus.PARTIALLY_PAID,
                CustomerInvoiceStatus.OVERDUE,
            ],
        ).first()
        if existing:
            return existing

        invoice = cls.create(
            customer=order.customer,
            actor=actor,
            order=order,
            notes=f"Invoice for order {order.order_number}",
        )
        for item in order.items.select_related("variant", "variant__product"):
            CustomerInvoiceLine.objects.create(
                invoice=invoice,
                description=item.product_name or item.variant.sku,
                quantity=item.quantity,
                unit_price_ex_gst_cents=item.unit_price_ex_gst_cents,
                line_ex_gst_cents=item.line_total_ex_gst_cents,
                line_gst_cents=item.line_gst_cents,
                order_item=item,
            )
        cls._recalculate_totals(invoice)
        return invoice

    @classmethod
    @transaction.atomic
    def add_line(
        cls,
        *,
        invoice: CustomerInvoice,
        description: str,
        quantity: int,
        unit_price_ex_gst_cents: int,
    ) -> CustomerInvoiceLine:
        if invoice.status != CustomerInvoiceStatus.DRAFT:
            raise BusinessRuleError("Cannot modify a non-draft invoice.")
        tax = TaxEngine.normalize(amount_cents=unit_price_ex_gst_cents, treatment="gst_exclusive")
        line = CustomerInvoiceLine.objects.create(
            invoice=invoice,
            description=description,
            quantity=quantity,
            unit_price_ex_gst_cents=unit_price_ex_gst_cents,
            line_ex_gst_cents=tax["amount_ex_gst_cents"] * quantity,
            line_gst_cents=tax["gst_cents"] * quantity,
        )
        cls._recalculate_totals(invoice)
        return line

    @classmethod
    @transaction.atomic
    def submit_for_approval(cls, *, invoice: CustomerInvoice, actor) -> CustomerInvoice:
        if invoice.status != CustomerInvoiceStatus.DRAFT:
            raise BusinessRuleError("Only draft invoices can be submitted.")
        if not invoice.lines.exists():
            raise BusinessRuleError("Invoice must have at least one line.")
        WorkflowEngine.start(
            definition_code=WorkflowCode.AR_INVOICE_APPROVAL,
            resource_type="customer_invoice",
            resource_id=str(invoice.public_id),
            actor=actor,
        )
        cls._audit(actor, invoice, "submit", f"Invoice {invoice.invoice_number} submitted for approval")
        return invoice

    @classmethod
    @transaction.atomic
    def issue(cls, *, invoice: CustomerInvoice, actor, issue_date: date | None = None) -> CustomerInvoice:
        if invoice.status not in (CustomerInvoiceStatus.DRAFT,):
            raise BusinessRuleError("Invoice cannot be issued from current status.")
        if not invoice.lines.exists():
            raise BusinessRuleError("Invoice must have at least one line.")

        today = issue_date or timezone.now().date()
        invoice.status = CustomerInvoiceStatus.ISSUED
        invoice.issue_date = today
        invoice.due_date = today + timedelta(days=invoice.payment_terms_days)
        invoice.issued_by = actor if getattr(actor, "is_authenticated", False) else None
        invoice.balance_due_cents = invoice.total_inc_gst_cents - invoice.amount_paid_cents
        invoice.save(
            update_fields=[
                "status",
                "issue_date",
                "due_date",
                "issued_by",
                "balance_due_cents",
                "updated_at",
            ]
        )

        payload = {
            "invoice_number": invoice.invoice_number,
            "total_inc_gst_cents": invoice.total_inc_gst_cents,
            "total_ex_gst_cents": invoice.subtotal_ex_gst_cents,
            "gst_cents": invoice.gst_cents,
        }
        DomainEventPublisher.publish(
            event_type=DomainEventType.AR_INVOICE_ISSUED,
            aggregate_type="customer_invoice",
            aggregate_id=str(invoice.public_id),
            payload=payload,
            idempotency_key=f"ar.invoice.issued:{invoice.public_id}",
        )
        cls._audit(actor, invoice, "issue", f"Invoice {invoice.invoice_number} issued")
        return invoice

    @classmethod
    @transaction.atomic
    def cancel(cls, *, invoice: CustomerInvoice, actor) -> CustomerInvoice:
        if invoice.status in (CustomerInvoiceStatus.PAID, CustomerInvoiceStatus.CANCELLED):
            raise BusinessRuleError("Cannot cancel a paid or already cancelled invoice.")
        if invoice.amount_paid_cents > 0:
            raise BusinessRuleError("Cannot cancel an invoice with payments applied.")
        invoice.status = CustomerInvoiceStatus.CANCELLED
        invoice.save(update_fields=["status", "updated_at"])
        cls._audit(actor, invoice, "cancel", f"Invoice {invoice.invoice_number} cancelled")
        return invoice

    @classmethod
    def refresh_overdue(cls) -> int:
        today = timezone.now().date()
        updated = CustomerInvoice.objects.filter(
            status__in=[CustomerInvoiceStatus.ISSUED, CustomerInvoiceStatus.PARTIALLY_PAID],
            due_date__lt=today,
            balance_due_cents__gt=0,
        ).update(status=CustomerInvoiceStatus.OVERDUE)
        return updated

    @staticmethod
    def _audit(user, invoice: CustomerInvoice, action: str, summary: str) -> None:
        AuditService.log(
            user=user,
            module=AuditModule.RECEIVABLES,
            action=action,
            resource_type="customer_invoice",
            resource_id=str(invoice.public_id),
            summary=summary,
            metadata={"invoice_number": invoice.invoice_number, "status": invoice.status},
            mirror_operational=False,
        )


class CustomerPaymentService:
    @classmethod
    @transaction.atomic
    def record_payment(
        cls,
        *,
        customer: Customer,
        amount_cents: int,
        payment_date: date,
        actor,
        payment_method: str = PaymentMethod.BANK_TRANSFER,
        reference: str = "",
        allocations: list[dict[str, Any]] | None = None,
    ) -> CustomerPayment:
        if amount_cents <= 0:
            raise BusinessRuleError("Payment amount must be positive.")

        payment = CustomerPayment.objects.create(
            payment_number=_next_payment_number(),
            customer=customer,
            payment_date=payment_date,
            amount_cents=amount_cents,
            payment_method=payment_method,
            reference=reference,
            recorded_by=actor if getattr(actor, "is_authenticated", False) else None,
        )

        allocated_total = 0
        for alloc in allocations or []:
            invoice_id = alloc.get("invoiceId") or alloc.get("invoice_id")
            invoice = CustomerInvoice.objects.filter(public_id=invoice_id).first()
            if not invoice or invoice.customer_id != customer.id:
                raise NotFoundError("Invoice not found for customer.")
            alloc_amount = int(alloc.get("amountCents") or alloc.get("amount_cents", 0))
            if alloc_amount <= 0:
                continue
            if alloc_amount > invoice.balance_due_cents:
                raise BusinessRuleError(
                    f"Allocation exceeds balance on {invoice.invoice_number}."
                )
            CustomerPaymentAllocation.objects.create(
                payment=payment,
                invoice=invoice,
                amount_cents=alloc_amount,
            )
            invoice.amount_paid_cents += alloc_amount
            invoice.balance_due_cents = invoice.total_inc_gst_cents - invoice.amount_paid_cents
            if invoice.balance_due_cents <= 0:
                invoice.status = CustomerInvoiceStatus.PAID
            else:
                invoice.status = CustomerInvoiceStatus.PARTIALLY_PAID
            invoice.save(
                update_fields=["amount_paid_cents", "balance_due_cents", "status", "updated_at"]
            )
            allocated_total += alloc_amount

        if allocated_total != amount_cents:
            raise BusinessRuleError(
                f"Allocations ({allocated_total}) must equal payment amount ({amount_cents})."
            )

        DomainEventPublisher.publish(
            event_type=DomainEventType.AR_PAYMENT_RECEIVED,
            aggregate_type="customer_payment",
            aggregate_id=str(payment.public_id),
            payload={
                "payment_number": payment.payment_number,
                "amount_cents": amount_cents,
            },
            idempotency_key=f"ar.payment.received:{payment.public_id}",
        )
        AccountingAuditService.log(
            user=actor,
            action="ar_payment",
            resource_type="customer_payment",
            resource_id=str(payment.public_id),
            summary=f"Payment {payment.payment_number} recorded",
            metadata={"amount_cents": amount_cents},
        )
        return payment


class CreditNoteService:
    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        customer: Customer,
        actor,
        invoice: CustomerInvoice | None = None,
        subtotal_ex_gst_cents: int,
        reason: str = "",
    ) -> CreditNote:
        tax = TaxEngine.normalize(amount_cents=subtotal_ex_gst_cents, treatment="gst_exclusive")
        cn = CreditNote.objects.create(
            credit_note_number=_next_credit_note_number(),
            customer=customer,
            invoice=invoice,
            subtotal_ex_gst_cents=tax["amount_ex_gst_cents"],
            gst_cents=tax["gst_cents"],
            total_inc_gst_cents=tax["amount_inc_gst_cents"],
            reason=reason,
            status=CreditNoteStatus.DRAFT,
        )
        return cn

    @classmethod
    @transaction.atomic
    def issue(cls, *, credit_note: CreditNote, actor) -> CreditNote:
        if credit_note.status != CreditNoteStatus.DRAFT:
            raise BusinessRuleError("Credit note already issued.")
        credit_note.status = CreditNoteStatus.ISSUED
        credit_note.issue_date = timezone.now().date()
        credit_note.issued_by = actor if getattr(actor, "is_authenticated", False) else None
        credit_note.save(update_fields=["status", "issue_date", "issued_by", "updated_at"])

        if credit_note.invoice_id:
            inv = credit_note.invoice
            inv.amount_paid_cents += credit_note.total_inc_gst_cents
            inv.balance_due_cents = max(0, inv.total_inc_gst_cents - inv.amount_paid_cents)
            if inv.balance_due_cents <= 0:
                inv.status = CustomerInvoiceStatus.PAID
            inv.save(update_fields=["amount_paid_cents", "balance_due_cents", "status", "updated_at"])

        DomainEventPublisher.publish(
            event_type=DomainEventType.AR_CREDIT_NOTE_ISSUED,
            aggregate_type="credit_note",
            aggregate_id=str(credit_note.public_id),
            payload={
                "credit_note_number": credit_note.credit_note_number,
                "total_ex_gst_cents": credit_note.subtotal_ex_gst_cents,
                "gst_cents": credit_note.gst_cents,
                "total_inc_gst_cents": credit_note.total_inc_gst_cents,
            },
            idempotency_key=f"ar.credit_note.issued:{credit_note.public_id}",
        )
        credit_note.status = CreditNoteStatus.APPLIED
        credit_note.save(update_fields=["status", "updated_at"])
        return credit_note


class ReceivablesReportingService:
    @staticmethod
    def customer_statement(*, customer: Customer) -> dict:
        invoices = CustomerInvoice.objects.filter(
            customer=customer,
            status__in=[
                CustomerInvoiceStatus.ISSUED,
                CustomerInvoiceStatus.PARTIALLY_PAID,
                CustomerInvoiceStatus.OVERDUE,
                CustomerInvoiceStatus.PAID,
            ],
        ).order_by("-issue_date")
        payments = CustomerPayment.objects.filter(customer=customer).order_by("-payment_date")

        outstanding = invoices.filter(
            status__in=[
                CustomerInvoiceStatus.ISSUED,
                CustomerInvoiceStatus.PARTIALLY_PAID,
                CustomerInvoiceStatus.OVERDUE,
            ],
            balance_due_cents__gt=0,
        ).aggregate(total=Sum("balance_due_cents"))["total"] or 0

        return {
            "customerId": str(customer.public_id),
            "outstandingBalanceCents": int(outstanding),
            "invoices": [
                {
                    "invoiceNumber": inv.invoice_number,
                    "issueDate": inv.issue_date.isoformat() if inv.issue_date else None,
                    "dueDate": inv.due_date.isoformat() if inv.due_date else None,
                    "totalIncGstCents": inv.total_inc_gst_cents,
                    "amountPaidCents": inv.amount_paid_cents,
                    "balanceDueCents": inv.balance_due_cents,
                    "status": inv.status,
                }
                for inv in invoices[:100]
            ],
            "payments": [
                {
                    "paymentNumber": p.payment_number,
                    "paymentDate": p.payment_date.isoformat(),
                    "amountCents": p.amount_cents,
                    "reference": p.reference,
                }
                for p in payments[:100]
            ],
        }

    @staticmethod
    def customer_aging(*, as_of: date | None = None) -> list[dict]:
        CustomerInvoiceService.refresh_overdue()
        as_of = as_of or timezone.now().date()
        open_invoices = CustomerInvoice.objects.filter(
            balance_due_cents__gt=0,
            status__in=[
                CustomerInvoiceStatus.ISSUED,
                CustomerInvoiceStatus.PARTIALLY_PAID,
                CustomerInvoiceStatus.OVERDUE,
            ],
            issue_date__isnull=False,
        ).select_related("customer", "customer__user")

        buckets: dict[str, dict] = {}
        for inv in open_invoices:
            cust_key = str(inv.customer.public_id)
            if cust_key not in buckets:
                display = (
                    inv.customer.user.email
                    if inv.customer.user_id
                    else str(inv.customer.public_id)
                )
                buckets[cust_key] = {
                    "customerId": cust_key,
                    "customerName": display,
                    "currentCents": 0,
                    "days31_60Cents": 0,
                    "days61_90Cents": 0,
                    "days91_120Cents": 0,
                    "days120PlusCents": 0,
                    "totalOutstandingCents": 0,
                }
            days_past = (as_of - inv.due_date).days if inv.due_date else 0
            amount = inv.balance_due_cents
            row = buckets[cust_key]
            if days_past <= 0:
                row["currentCents"] += amount
            elif days_past <= 30:
                row["currentCents"] += amount
            elif days_past <= 60:
                row["days31_60Cents"] += amount
            elif days_past <= 90:
                row["days61_90Cents"] += amount
            elif days_past <= 120:
                row["days91_120Cents"] += amount
            else:
                row["days120PlusCents"] += amount
            row["totalOutstandingCents"] += amount

        return sorted(buckets.values(), key=lambda r: -r["totalOutstandingCents"])

    @staticmethod
    def ar_summary() -> dict:
        CustomerInvoiceService.refresh_overdue()
        qs = CustomerInvoice.objects.exclude(status=CustomerInvoiceStatus.CANCELLED)
        outstanding = qs.filter(
            status__in=[
                CustomerInvoiceStatus.ISSUED,
                CustomerInvoiceStatus.PARTIALLY_PAID,
                CustomerInvoiceStatus.OVERDUE,
            ],
            balance_due_cents__gt=0,
        ).aggregate(total=Sum("balance_due_cents"))["total"] or 0
        overdue = qs.filter(status=CustomerInvoiceStatus.OVERDUE).aggregate(
            total=Sum("balance_due_cents")
        )["total"] or 0
        paid_mtd = qs.filter(
            status=CustomerInvoiceStatus.PAID,
            issue_date__gte=timezone.now().date().replace(day=1),
        ).aggregate(total=Sum("total_inc_gst_cents"))["total"] or 0
        return {
            "totalOutstandingCents": int(outstanding),
            "overdueCents": int(overdue),
            "paidMonthToDateCents": int(paid_mtd),
            "openInvoiceCount": qs.filter(
                balance_due_cents__gt=0,
                status__in=[
                    CustomerInvoiceStatus.ISSUED,
                    CustomerInvoiceStatus.PARTIALLY_PAID,
                    CustomerInvoiceStatus.OVERDUE,
                ],
            ).count(),
        }
