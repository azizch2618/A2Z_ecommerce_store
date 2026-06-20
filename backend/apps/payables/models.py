"""Accounts Payable models — supplier invoices, payments, debit notes."""
from django.db import models

from apps.core.models import PublicIdModel
from apps.payables.constants import DebitNoteStatus, MatchStatus, SupplierInvoiceStatus


class SupplierInvoice(PublicIdModel):
    invoice_number = models.CharField(max_length=30, unique=True)
    supplier_invoice_ref = models.CharField(max_length=100, blank=True)
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.RESTRICT,
        related_name="invoices",
    )
    purchase_order = models.ForeignKey(
        "suppliers.PurchaseOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_invoices",
    )
    goods_receipt = models.ForeignKey(
        "procurement.GoodsReceipt",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_invoices",
    )
    status = models.CharField(
        max_length=20,
        choices=SupplierInvoiceStatus.choices,
        default=SupplierInvoiceStatus.DRAFT,
        db_index=True,
    )
    match_status = models.CharField(
        max_length=20,
        choices=MatchStatus.choices,
        default=MatchStatus.UNMATCHED,
    )
    invoice_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    subtotal_ex_gst_cents = models.BigIntegerField(default=0)
    gst_cents = models.BigIntegerField(default=0)
    total_inc_gst_cents = models.BigIntegerField(default=0)
    amount_paid_cents = models.BigIntegerField(default=0)
    balance_due_cents = models.BigIntegerField(default=0)
    currency_code = models.CharField(max_length=3, default="AUD")
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_supplier_invoices",
    )
    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_invoices",
    )

    class Meta:
        db_table = "payables_supplier_invoices"
        ordering = ["-invoice_date", "-created_at"]
        indexes = [
            models.Index(fields=["status", "due_date"], name="idx_ap_inv_status_due"),
            models.Index(fields=["supplier", "status"], name="idx_ap_inv_supplier"),
        ]

    def __str__(self) -> str:
        return self.invoice_number


class SupplierInvoiceLine(PublicIdModel):
    invoice = models.ForeignKey(
        SupplierInvoice,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    purchase_order_line = models.ForeignKey(
        "suppliers.PurchaseOrderLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_lines",
    )
    goods_receipt_line = models.ForeignKey(
        "procurement.GoodsReceiptLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_lines",
    )
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_cost_ex_gst_cents = models.BigIntegerField()
    line_ex_gst_cents = models.BigIntegerField()
    line_gst_cents = models.BigIntegerField(default=0)

    class Meta:
        db_table = "payables_supplier_invoice_lines"
        ordering = ["invoice", "id"]


class SupplierPayment(PublicIdModel):
    payment_number = models.CharField(max_length=30, unique=True)
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.RESTRICT,
        related_name="payments",
    )
    payment_date = models.DateField()
    amount_cents = models.BigIntegerField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_supplier_payments",
    )
    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_payments",
    )

    class Meta:
        db_table = "payables_supplier_payments"
        ordering = ["-payment_date", "-created_at"]


class SupplierPaymentAllocation(PublicIdModel):
    payment = models.ForeignKey(
        SupplierPayment,
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    invoice = models.ForeignKey(
        SupplierInvoice,
        on_delete=models.RESTRICT,
        related_name="payment_allocations",
    )
    amount_cents = models.BigIntegerField()

    class Meta:
        db_table = "payables_payment_allocations"
        unique_together = [("payment", "invoice")]


class DebitNote(PublicIdModel):
    debit_note_number = models.CharField(max_length=30, unique=True)
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.RESTRICT,
        related_name="debit_notes",
    )
    invoice = models.ForeignKey(
        SupplierInvoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="debit_notes",
    )
    status = models.CharField(
        max_length=20,
        choices=DebitNoteStatus.choices,
        default=DebitNoteStatus.DRAFT,
    )
    issue_date = models.DateField(null=True, blank=True)
    subtotal_ex_gst_cents = models.BigIntegerField(default=0)
    gst_cents = models.BigIntegerField(default=0)
    total_inc_gst_cents = models.BigIntegerField(default=0)
    reason = models.TextField(blank=True)
    issued_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_debit_notes",
    )
    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="debit_notes",
    )

    class Meta:
        db_table = "payables_debit_notes"
        ordering = ["-issue_date", "-created_at"]
