"""Accounts Receivable models — customer invoices, payments, credit notes."""
from django.db import models

from apps.core.models import PublicIdModel
from apps.receivables.constants import CreditNoteStatus, CustomerInvoiceStatus, PaymentMethod


class CustomerInvoice(PublicIdModel):
    invoice_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.RESTRICT,
        related_name="invoices",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    status = models.CharField(
        max_length=20,
        choices=CustomerInvoiceStatus.choices,
        default=CustomerInvoiceStatus.DRAFT,
        db_index=True,
    )
    issue_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    payment_terms_days = models.PositiveIntegerField(default=30)
    subtotal_ex_gst_cents = models.BigIntegerField(default=0)
    gst_cents = models.BigIntegerField(default=0)
    total_inc_gst_cents = models.BigIntegerField(default=0)
    amount_paid_cents = models.BigIntegerField(default=0)
    balance_due_cents = models.BigIntegerField(default=0)
    currency_code = models.CharField(max_length=3, default="AUD")
    notes = models.TextField(blank=True)
    issued_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_customer_invoices",
    )
    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_invoices",
    )

    class Meta:
        db_table = "receivables_customer_invoices"
        ordering = ["-issue_date", "-created_at"]
        indexes = [
            models.Index(fields=["status", "due_date"], name="idx_ar_inv_status_due"),
            models.Index(fields=["customer", "status"], name="idx_ar_inv_customer"),
        ]

    def __str__(self) -> str:
        return self.invoice_number


class CustomerInvoiceLine(PublicIdModel):
    invoice = models.ForeignKey(
        CustomerInvoice,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_ex_gst_cents = models.BigIntegerField()
    line_ex_gst_cents = models.BigIntegerField()
    line_gst_cents = models.BigIntegerField(default=0)
    order_item = models.ForeignKey(
        "orders.OrderItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoice_lines",
    )

    class Meta:
        db_table = "receivables_customer_invoice_lines"
        ordering = ["invoice", "id"]


class CustomerPayment(PublicIdModel):
    payment_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.RESTRICT,
        related_name="payments",
    )
    payment_date = models.DateField()
    amount_cents = models.BigIntegerField()
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER,
    )
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_customer_payments",
    )
    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_payments",
    )

    class Meta:
        db_table = "receivables_customer_payments"
        ordering = ["-payment_date", "-created_at"]


class CustomerPaymentAllocation(PublicIdModel):
    payment = models.ForeignKey(
        CustomerPayment,
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    invoice = models.ForeignKey(
        CustomerInvoice,
        on_delete=models.RESTRICT,
        related_name="payment_allocations",
    )
    amount_cents = models.BigIntegerField()

    class Meta:
        db_table = "receivables_payment_allocations"
        unique_together = [("payment", "invoice")]


class CreditNote(PublicIdModel):
    credit_note_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.RESTRICT,
        related_name="credit_notes",
    )
    invoice = models.ForeignKey(
        CustomerInvoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="credit_notes",
    )
    status = models.CharField(
        max_length=20,
        choices=CreditNoteStatus.choices,
        default=CreditNoteStatus.DRAFT,
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
        related_name="issued_credit_notes",
    )
    journal_entry = models.ForeignKey(
        "accounting.JournalEntry",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="credit_notes",
    )

    class Meta:
        db_table = "receivables_credit_notes"
        ordering = ["-issue_date", "-created_at"]
