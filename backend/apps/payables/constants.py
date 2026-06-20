from django.db import models


class SupplierInvoiceStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    MATCHED = "matched", "Matched"
    APPROVED = "approved", "Approved"
    PARTIALLY_PAID = "partially_paid", "Partially Paid"
    PAID = "paid", "Paid"
    CANCELLED = "cancelled", "Cancelled"


class MatchStatus(models.TextChoices):
    UNMATCHED = "unmatched", "Unmatched"
    PARTIAL = "partial", "Partial Match"
    MATCHED = "matched", "Fully Matched"
    EXCEPTION = "exception", "Exception"


class DebitNoteStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ISSUED = "issued", "Issued"
    APPLIED = "applied", "Applied"
    CANCELLED = "cancelled", "Cancelled"
