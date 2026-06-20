from django.db import models


class CustomerInvoiceStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ISSUED = "issued", "Issued"
    PARTIALLY_PAID = "partially_paid", "Partially Paid"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"


class CreditNoteStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ISSUED = "issued", "Issued"
    APPLIED = "applied", "Applied"
    CANCELLED = "cancelled", "Cancelled"


class PaymentMethod(models.TextChoices):
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    CARD = "card", "Card"
    CASH = "cash", "Cash"
    TRADE_CREDIT = "trade_credit", "Trade Credit"
    OTHER = "other", "Other"


# Aging bucket labels (days past due)
AGING_BUCKETS = (
    (30, "current"),
    (60, "31_60"),
    (90, "61_90"),
    (120, "91_120"),
    (None, "120_plus"),
)
