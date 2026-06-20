"""Procurement module constants."""
from django.db import models


class PurchaseRequestPriority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    URGENT = "urgent", "Urgent"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SCHEDULED = "scheduled", "Scheduled"
    PARTIAL = "partial", "Partially Paid"
    PAID = "paid", "Paid"


class SupplierDocumentType(models.TextChoices):
    INVOICE = "invoice", "Invoice"
    PACKING_SLIP = "packing_slip", "Packing Slip"
    CERTIFICATE = "certificate", "Certificate"
    OTHER = "other", "Other"
