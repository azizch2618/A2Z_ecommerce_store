"""Supplier and purchase order models."""
from django.db import models

from apps.core.models import PublicIdModel
from apps.core.validators import validate_abn


class Supplier(PublicIdModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    abn = models.CharField(max_length=11, blank=True, validators=[validate_abn])
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    payment_terms_days = models.PositiveIntegerField(default=30)
    currency_code = models.CharField(max_length=3, default="AUD")
    is_active = models.BooleanField(default=True)
    contact_details = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "suppliers"

    def __str__(self) -> str:
        return self.name


class SupplierProduct(PublicIdModel):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="supplier_products")
    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.CASCADE, related_name="supplier_products")
    supplier_sku = models.CharField(max_length=50, blank=True)
    cost_price_cents = models.BigIntegerField()
    lead_time_days = models.PositiveIntegerField(null=True, blank=True)
    min_order_quantity = models.PositiveIntegerField(default=1)
    is_preferred = models.BooleanField(default=False)

    class Meta:
        db_table = "supplier_products"
        unique_together = [("supplier", "variant")]


class PurchaseOrder(PublicIdModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        CONFIRMED = "confirmed", "Confirmed"
        PARTIAL_RECEIVED = "partial_received", "Partial Received"
        RECEIVED = "received", "Received"
        CANCELLED = "cancelled", "Cancelled"

    po_number = models.CharField(max_length=20, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.RESTRICT, related_name="purchase_orders")
    warehouse = models.ForeignKey("inventory.Warehouse", on_delete=models.RESTRICT, related_name="purchase_orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_ex_gst_cents = models.BigIntegerField(default=0)
    expected_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_orders",
    )

    class Meta:
        db_table = "purchase_orders"


class PurchaseOrderLine(PublicIdModel):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="lines")
    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.RESTRICT)
    quantity_ordered = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)
    unit_cost_cents = models.BigIntegerField()

    class Meta:
        db_table = "purchase_order_lines"
