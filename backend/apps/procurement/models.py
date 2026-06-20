"""Procurement — requisitions, goods receipts, supplier portal."""
from django.db import models

from apps.core.models import PublicIdModel
from apps.procurement.constants import (
    PaymentStatus,
    PurchaseRequestPriority,
    SupplierDocumentType,
)


class SupplierMembership(PublicIdModel):
    """Links a user account to a supplier for portal access."""

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="supplier_memberships",
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "procurement_supplier_memberships"
        unique_together = [("user", "supplier")]


class PurchaseRequest(PublicIdModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CONVERTED = "converted", "Converted"

    request_number = models.CharField(max_length=20, unique=True)
    requested_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="purchase_requests",
    )
    department = models.ForeignKey(
        "erp.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_requests",
    )
    cost_center = models.ForeignKey(
        "erp.CostCenter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_requests",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.RESTRICT,
        related_name="purchase_requests",
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_requests",
    )
    priority = models.CharField(
        max_length=10,
        choices=PurchaseRequestPriority.choices,
        default=PurchaseRequestPriority.MEDIUM,
    )
    justification = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )
    converted_po = models.OneToOneField(
        "suppliers.PurchaseOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_request",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "procurement_purchase_requests"
        ordering = ["-created_at"]


class PurchaseRequestLine(PublicIdModel):
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.RESTRICT)
    sku = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_cost_cents = models.BigIntegerField(default=0)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = "procurement_purchase_request_lines"


class GoodsReceipt(PublicIdModel):
    class Status(models.TextChoices):
        PARTIAL = "partial", "Partial"
        FULL = "full", "Full"

    grn_number = models.CharField(max_length=20, unique=True)
    purchase_order = models.ForeignKey(
        "suppliers.PurchaseOrder",
        on_delete=models.CASCADE,
        related_name="goods_receipts",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.RESTRICT,
        related_name="goods_receipts",
    )
    status = models.CharField(max_length=10, choices=Status.choices)
    received_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="goods_receipts",
    )
    received_at = models.DateTimeField()
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "procurement_goods_receipts"
        ordering = ["-received_at"]


class GoodsReceiptLine(PublicIdModel):
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    purchase_order_line = models.ForeignKey(
        "suppliers.PurchaseOrderLine",
        on_delete=models.RESTRICT,
        related_name="receipt_lines",
    )
    quantity_received = models.PositiveIntegerField()
    batch_number = models.CharField(max_length=50, blank=True)
    received_at = models.DateTimeField()

    class Meta:
        db_table = "procurement_goods_receipt_lines"


class SupplierDocument(PublicIdModel):
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="documents",
    )
    purchase_order = models.ForeignKey(
        "suppliers.PurchaseOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supplier_documents",
    )
    document_type = models.CharField(
        max_length=20,
        choices=SupplierDocumentType.choices,
        default=SupplierDocumentType.OTHER,
    )
    file = models.FileField(upload_to="supplier_documents/%Y/%m/")
    original_filename = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="supplier_documents_uploaded",
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "procurement_supplier_documents"
        ordering = ["-created_at"]
