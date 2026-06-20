"""Accounts Payable business logic."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet, Sum
from django.utils import timezone

from apps.accounting.audit import AccountingAuditService
from apps.accounting.tax import TaxEngine
from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.core.resolvers import resolve_supplier
from apps.erp.constants import AuditModule, DocumentType, DomainEventType, WorkflowCode
from apps.erp.services.audit import AuditService
from apps.erp.services.document_sequence import DocumentSequenceService
from apps.erp.services.events import DomainEventPublisher
from apps.erp.services.party import PartyService
from apps.erp.services.workflow import WorkflowEngine
from apps.payables.constants import DebitNoteStatus, MatchStatus, SupplierInvoiceStatus
from apps.payables.models import (
    DebitNote,
    SupplierInvoice,
    SupplierInvoiceLine,
    SupplierPayment,
    SupplierPaymentAllocation,
)
from apps.procurement.models import GoodsReceipt
from apps.suppliers.models import PurchaseOrder, PurchaseOrderLine, Supplier


def _next_ap_invoice_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.AP_INVOICE)


def _next_ap_payment_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.AP_PAYMENT)


def _next_debit_note_number() -> str:
    return DocumentSequenceService.next_number(DocumentType.DEBIT_NOTE)


class SupplierInvoiceService:
    @staticmethod
    def list_invoices(
        *,
        status: str | None = None,
        supplier_id: UUID | None = None,
    ) -> QuerySet[SupplierInvoice]:
        qs = SupplierInvoice.objects.select_related(
            "supplier", "purchase_order", "goods_receipt", "approved_by"
        ).prefetch_related("lines")
        if status:
            qs = qs.filter(status=status)
        if supplier_id:
            qs = qs.filter(supplier__public_id=supplier_id)
        return qs.order_by("-created_at")

    @staticmethod
    def get_invoice(public_id: UUID) -> SupplierInvoice:
        inv = SupplierInvoiceService.list_invoices().filter(public_id=public_id).first()
        if not inv:
            raise NotFoundError("Supplier invoice not found.")
        return inv

    @classmethod
    def _recalculate_totals(cls, invoice: SupplierInvoice) -> None:
        lines = invoice.lines.all()
        subtotal = sum(line.line_ex_gst_cents for line in lines)
        gst = sum(line.line_gst_cents for line in lines)
        total = subtotal + gst
        invoice.subtotal_ex_gst_cents = subtotal
        invoice.gst_cents = gst
        invoice.total_inc_gst_cents = total
        invoice.balance_due_cents = max(0, total - invoice.amount_paid_cents)
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
    def create_from_po(
        cls,
        *,
        purchase_order: PurchaseOrder,
        actor,
        supplier_invoice_ref: str = "",
        goods_receipt: GoodsReceipt | None = None,
    ) -> SupplierInvoice:
        if purchase_order.status == PurchaseOrder.Status.CANCELLED:
            raise BusinessRuleError("Cannot invoice a cancelled PO.")
        existing = SupplierInvoice.objects.filter(
            purchase_order=purchase_order,
            status__in=[
                SupplierInvoiceStatus.DRAFT,
                SupplierInvoiceStatus.SUBMITTED,
                SupplierInvoiceStatus.MATCHED,
                SupplierInvoiceStatus.APPROVED,
                SupplierInvoiceStatus.PARTIALLY_PAID,
            ],
        ).first()
        if existing:
            return existing

        supplier = purchase_order.supplier
        terms = supplier.payment_terms_days or 30
        invoice = SupplierInvoice.objects.create(
            invoice_number=_next_ap_invoice_number(),
            supplier_invoice_ref=supplier_invoice_ref,
            supplier=supplier,
            purchase_order=purchase_order,
            goods_receipt=goods_receipt,
            status=SupplierInvoiceStatus.DRAFT,
            invoice_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=terms),
        )
        PartyService.ensure_for_supplier(supplier)

        for po_line in purchase_order.lines.select_related("variant"):
            qty = po_line.quantity_received or po_line.quantity_ordered
            if qty <= 0:
                continue
            tax = TaxEngine.normalize(amount_cents=po_line.unit_cost_cents, treatment="gst_exclusive")
            line_ex = tax["amount_ex_gst_cents"] * qty
            line_gst = tax["gst_cents"] * qty
            SupplierInvoiceLine.objects.create(
                invoice=invoice,
                purchase_order_line=po_line,
                description=po_line.variant.sku,
                quantity=qty,
                unit_cost_ex_gst_cents=po_line.unit_cost_cents,
                line_ex_gst_cents=line_ex,
                line_gst_cents=line_gst,
            )
        cls._recalculate_totals(invoice)
        cls._audit(actor, invoice, "create", f"AP invoice {invoice.invoice_number} from PO {purchase_order.po_number}")
        return invoice

    @classmethod
    @transaction.atomic
    def submit(cls, *, invoice: SupplierInvoice, actor) -> SupplierInvoice:
        if invoice.status != SupplierInvoiceStatus.DRAFT:
            raise BusinessRuleError("Only draft invoices can be submitted.")
        if not invoice.lines.exists():
            raise BusinessRuleError("Invoice must have lines.")
        invoice.status = SupplierInvoiceStatus.SUBMITTED
        invoice.save(update_fields=["status", "updated_at"])
        WorkflowEngine.start(
            definition_code=WorkflowCode.AP_INVOICE_APPROVAL,
            resource_type="supplier_invoice",
            resource_id=str(invoice.public_id),
            actor=actor,
        )
        cls._audit(actor, invoice, "submit", f"AP invoice {invoice.invoice_number} submitted")
        return invoice

    @classmethod
    @transaction.atomic
    def match(cls, *, invoice: SupplierInvoice, actor) -> SupplierInvoice:
        """Three-way match: PO quantities/costs vs invoice lines vs GRN received qty."""
        if invoice.status not in (
            SupplierInvoiceStatus.SUBMITTED,
            SupplierInvoiceStatus.DRAFT,
            SupplierInvoiceStatus.MATCHED,
        ):
            raise BusinessRuleError("Invoice cannot be matched in current status.")

        po = invoice.purchase_order
        if not po:
            invoice.match_status = MatchStatus.EXCEPTION
            invoice.save(update_fields=["match_status", "updated_at"])
            raise BusinessRuleError("No purchase order linked for matching.")

        exceptions = []
        for line in invoice.lines.select_related("purchase_order_line"):
            po_line = line.purchase_order_line
            if not po_line:
                exceptions.append(f"Line {line.description} not linked to PO")
                continue
            if line.quantity > po_line.quantity_received:
                exceptions.append(
                    f"{line.description}: invoiced qty {line.quantity} > received {po_line.quantity_received}"
                )
            if line.unit_cost_ex_gst_cents != po_line.unit_cost_cents:
                exceptions.append(
                    f"{line.description}: unit cost mismatch"
                )

        if exceptions:
            invoice.match_status = MatchStatus.EXCEPTION
            invoice.save(update_fields=["match_status", "updated_at"])
            raise ConflictError("; ".join(exceptions))

        invoice.match_status = MatchStatus.MATCHED
        invoice.status = SupplierInvoiceStatus.MATCHED
        invoice.save(update_fields=["match_status", "status", "updated_at"])
        cls._audit(actor, invoice, "match", f"AP invoice {invoice.invoice_number} matched to PO/GRN")
        return invoice

    @classmethod
    @transaction.atomic
    def approve(cls, *, invoice: SupplierInvoice, actor) -> SupplierInvoice:
        if invoice.status not in (SupplierInvoiceStatus.MATCHED, SupplierInvoiceStatus.SUBMITTED):
            raise BusinessRuleError("Invoice must be matched or submitted before approval.")
        if invoice.match_status not in (MatchStatus.MATCHED, MatchStatus.PARTIAL):
            cls.match(invoice=invoice, actor=actor)

        invoice.status = SupplierInvoiceStatus.APPROVED
        invoice.approved_by = actor if getattr(actor, "is_authenticated", False) else None
        invoice.balance_due_cents = invoice.total_inc_gst_cents - invoice.amount_paid_cents
        invoice.save(
            update_fields=["status", "approved_by", "balance_due_cents", "updated_at"]
        )

        payload = {
            "invoice_number": invoice.invoice_number,
            "total_ex_gst_cents": invoice.subtotal_ex_gst_cents,
            "gst_cents": invoice.gst_cents,
            "total_inc_gst_cents": invoice.total_inc_gst_cents,
        }
        DomainEventPublisher.publish(
            event_type=DomainEventType.AP_INVOICE_APPROVED,
            aggregate_type="supplier_invoice",
            aggregate_id=str(invoice.public_id),
            payload=payload,
            idempotency_key=f"ap.invoice.approved:{invoice.public_id}",
        )
        cls._audit(actor, invoice, "approve", f"AP invoice {invoice.invoice_number} approved")
        return invoice

    @classmethod
    @transaction.atomic
    def cancel(cls, *, invoice: SupplierInvoice, actor) -> SupplierInvoice:
        if invoice.status in (SupplierInvoiceStatus.PAID, SupplierInvoiceStatus.CANCELLED):
            raise BusinessRuleError("Cannot cancel paid or cancelled invoice.")
        if invoice.amount_paid_cents > 0:
            raise BusinessRuleError("Cannot cancel invoice with payments.")
        invoice.status = SupplierInvoiceStatus.CANCELLED
        invoice.save(update_fields=["status", "updated_at"])
        cls._audit(actor, invoice, "cancel", f"AP invoice {invoice.invoice_number} cancelled")
        return invoice

    @staticmethod
    def _audit(user, invoice: SupplierInvoice, action: str, summary: str) -> None:
        AuditService.log(
            user=user,
            module=AuditModule.PAYABLES,
            action=action,
            resource_type="supplier_invoice",
            resource_id=str(invoice.public_id),
            summary=summary,
            metadata={"invoice_number": invoice.invoice_number, "status": invoice.status},
            mirror_operational=False,
        )


class SupplierPaymentService:
    @classmethod
    @transaction.atomic
    def record_payment(
        cls,
        *,
        supplier: Supplier,
        amount_cents: int,
        payment_date: date,
        actor,
        reference: str = "",
        allocations: list[dict[str, Any]] | None = None,
    ) -> SupplierPayment:
        if amount_cents <= 0:
            raise BusinessRuleError("Payment amount must be positive.")

        payment = SupplierPayment.objects.create(
            payment_number=_next_ap_payment_number(),
            supplier=supplier,
            payment_date=payment_date,
            amount_cents=amount_cents,
            reference=reference,
            recorded_by=actor if getattr(actor, "is_authenticated", False) else None,
        )

        allocated_total = 0
        for alloc in allocations or []:
            invoice_id = alloc.get("invoiceId") or alloc.get("invoice_id")
            invoice = SupplierInvoice.objects.filter(public_id=invoice_id).first()
            if not invoice or invoice.supplier_id != supplier.id:
                raise NotFoundError("Invoice not found for supplier.")
            if invoice.status not in (
                SupplierInvoiceStatus.APPROVED,
                SupplierInvoiceStatus.PARTIALLY_PAID,
            ):
                raise BusinessRuleError(f"Invoice {invoice.invoice_number} is not approved.")
            alloc_amount = int(alloc.get("amountCents") or alloc.get("amount_cents", 0))
            if alloc_amount <= 0:
                continue
            if alloc_amount > invoice.balance_due_cents:
                raise BusinessRuleError("Allocation exceeds invoice balance.")
            SupplierPaymentAllocation.objects.create(
                payment=payment,
                invoice=invoice,
                amount_cents=alloc_amount,
            )
            invoice.amount_paid_cents += alloc_amount
            invoice.balance_due_cents = invoice.total_inc_gst_cents - invoice.amount_paid_cents
            invoice.status = (
                SupplierInvoiceStatus.PAID
                if invoice.balance_due_cents <= 0
                else SupplierInvoiceStatus.PARTIALLY_PAID
            )
            invoice.save(
                update_fields=["amount_paid_cents", "balance_due_cents", "status", "updated_at"]
            )
            allocated_total += alloc_amount

        if allocated_total != amount_cents:
            raise BusinessRuleError("Allocations must equal payment amount.")

        DomainEventPublisher.publish(
            event_type=DomainEventType.AP_PAYMENT_MADE,
            aggregate_type="supplier_payment",
            aggregate_id=str(payment.public_id),
            payload={
                "payment_number": payment.payment_number,
                "amount_cents": amount_cents,
            },
            idempotency_key=f"ap.payment.made:{payment.public_id}",
        )
        AccountingAuditService.log(
            user=actor,
            action="ap_payment",
            resource_type="supplier_payment",
            resource_id=str(payment.public_id),
            summary=f"Supplier payment {payment.payment_number} recorded",
            metadata={"amount_cents": amount_cents},
        )
        return payment


class DebitNoteService:
    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        supplier: Supplier,
        actor,
        invoice: SupplierInvoice | None = None,
        subtotal_ex_gst_cents: int,
        reason: str = "",
    ) -> DebitNote:
        tax = TaxEngine.normalize(amount_cents=subtotal_ex_gst_cents, treatment="gst_exclusive")
        return DebitNote.objects.create(
            debit_note_number=_next_debit_note_number(),
            supplier=supplier,
            invoice=invoice,
            subtotal_ex_gst_cents=tax["amount_ex_gst_cents"],
            gst_cents=tax["gst_cents"],
            total_inc_gst_cents=tax["amount_inc_gst_cents"],
            reason=reason,
            status=DebitNoteStatus.DRAFT,
        )

    @classmethod
    @transaction.atomic
    def issue(cls, *, debit_note: DebitNote, actor) -> DebitNote:
        if debit_note.status != DebitNoteStatus.DRAFT:
            raise BusinessRuleError("Debit note already issued.")
        debit_note.status = DebitNoteStatus.ISSUED
        debit_note.issue_date = timezone.now().date()
        debit_note.issued_by = actor if getattr(actor, "is_authenticated", False) else None
        debit_note.save(update_fields=["status", "issue_date", "issued_by", "updated_at"])

        if debit_note.invoice_id:
            inv = debit_note.invoice
            inv.amount_paid_cents += debit_note.total_inc_gst_cents
            inv.balance_due_cents = max(0, inv.total_inc_gst_cents - inv.amount_paid_cents)
            if inv.balance_due_cents <= 0:
                inv.status = SupplierInvoiceStatus.PAID
            inv.save(update_fields=["amount_paid_cents", "balance_due_cents", "status", "updated_at"])

        DomainEventPublisher.publish(
            event_type=DomainEventType.AP_DEBIT_NOTE_ISSUED,
            aggregate_type="debit_note",
            aggregate_id=str(debit_note.public_id),
            payload={
                "debit_note_number": debit_note.debit_note_number,
                "total_ex_gst_cents": debit_note.subtotal_ex_gst_cents,
                "gst_cents": debit_note.gst_cents,
                "total_inc_gst_cents": debit_note.total_inc_gst_cents,
            },
            idempotency_key=f"ap.debit_note.issued:{debit_note.public_id}",
        )
        debit_note.status = DebitNoteStatus.APPLIED
        debit_note.save(update_fields=["status", "updated_at"])
        return debit_note


class PayablesReportingService:
    @staticmethod
    def supplier_statement(*, supplier: Supplier) -> dict:
        invoices = SupplierInvoice.objects.filter(
            supplier=supplier,
            status__in=[
                SupplierInvoiceStatus.APPROVED,
                SupplierInvoiceStatus.PARTIALLY_PAID,
                SupplierInvoiceStatus.PAID,
            ],
        ).order_by("-invoice_date")
        payments = SupplierPayment.objects.filter(supplier=supplier).order_by("-payment_date")
        outstanding = invoices.filter(
            status__in=[SupplierInvoiceStatus.APPROVED, SupplierInvoiceStatus.PARTIALLY_PAID],
            balance_due_cents__gt=0,
        ).aggregate(total=Sum("balance_due_cents"))["total"] or 0

        return {
            "supplierId": str(supplier.public_id),
            "supplierName": supplier.name,
            "outstandingBalanceCents": int(outstanding),
            "invoices": [
                {
                    "invoiceNumber": inv.invoice_number,
                    "supplierInvoiceRef": inv.supplier_invoice_ref,
                    "invoiceDate": inv.invoice_date.isoformat() if inv.invoice_date else None,
                    "dueDate": inv.due_date.isoformat() if inv.due_date else None,
                    "totalIncGstCents": inv.total_inc_gst_cents,
                    "balanceDueCents": inv.balance_due_cents,
                    "status": inv.status,
                    "matchStatus": inv.match_status,
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
    def supplier_aging(*, as_of: date | None = None) -> list[dict]:
        as_of = as_of or timezone.now().date()
        open_invoices = SupplierInvoice.objects.filter(
            balance_due_cents__gt=0,
            status__in=[SupplierInvoiceStatus.APPROVED, SupplierInvoiceStatus.PARTIALLY_PAID],
            due_date__isnull=False,
        ).select_related("supplier")

        buckets: dict[str, dict] = {}
        for inv in open_invoices:
            key = str(inv.supplier.public_id)
            if key not in buckets:
                buckets[key] = {
                    "supplierId": key,
                    "supplierName": inv.supplier.name,
                    "currentCents": 0,
                    "days31_60Cents": 0,
                    "days61_90Cents": 0,
                    "days91_120Cents": 0,
                    "days120PlusCents": 0,
                    "totalOutstandingCents": 0,
                }
            days_past = (as_of - inv.due_date).days
            amount = inv.balance_due_cents
            row = buckets[key]
            if days_past <= 30:
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
    def ap_summary() -> dict:
        qs = SupplierInvoice.objects.exclude(status=SupplierInvoiceStatus.CANCELLED)
        outstanding = qs.filter(
            status__in=[SupplierInvoiceStatus.APPROVED, SupplierInvoiceStatus.PARTIALLY_PAID],
            balance_due_cents__gt=0,
        ).aggregate(total=Sum("balance_due_cents"))["total"] or 0
        pending_match = qs.filter(
            status__in=[SupplierInvoiceStatus.SUBMITTED, SupplierInvoiceStatus.DRAFT]
        ).count()
        return {
            "totalOutstandingCents": int(outstanding),
            "pendingMatchCount": pending_match,
            "openInvoiceCount": qs.filter(
                balance_due_cents__gt=0,
                status__in=[SupplierInvoiceStatus.APPROVED, SupplierInvoiceStatus.PARTIALLY_PAID],
            ).count(),
        }
