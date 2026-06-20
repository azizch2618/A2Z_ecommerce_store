"""Warehouse, inventory positions, and stock movement ledger."""
import uuid

from django.db import models

from apps.core.models import PublicIdModel


class Warehouse(PublicIdModel):
    class WarehouseType(models.TextChoices):
        DISTRIBUTION = "distribution", "Distribution"
        RETAIL = "retail", "Retail"
        THIRD_PARTY = "3pl", "3PL"

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    warehouse_type = models.CharField(max_length=20, choices=WarehouseType.choices)
    address_line1 = models.CharField(max_length=255, blank=True)
    suburb = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=3, blank=True)
    postcode = models.CharField(max_length=4, blank=True)
    is_active = models.BooleanField(default=True)
    allows_pickup = models.BooleanField(default=False)
    capacity_units = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "warehouses"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code


class InventoryLevel(PublicIdModel):
    """Current stock position per warehouse and SKU (variant)."""

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="inventory_levels",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.CASCADE,
        related_name="inventory_levels",
    )
    quantity_on_hand = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0)
    average_cost_cents = models.BigIntegerField(default=0)
    last_cost_cents = models.BigIntegerField(default=0)
    last_sale_price_cents = models.BigIntegerField(default=0)
    reorder_point = models.IntegerField(default=0)
    reorder_quantity = models.IntegerField(default=0)
    last_counted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inventory_levels"
        unique_together = [("warehouse", "variant")]
        indexes = [
            models.Index(fields=["variant"], name="idx_inventory_variant"),
            models.Index(fields=["warehouse"], name="idx_inventory_warehouse"),
        ]

    @property
    def quantity_available(self) -> int:
        return max(self.quantity_on_hand - self.quantity_reserved, 0)

    @property
    def sku(self) -> str:
        return self.variant.sku


class Inventory(InventoryLevel):
    """ERP alias for inventory position records."""

    class Meta:
        proxy = True
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory"


class InventoryTransaction(PublicIdModel):
    """Append-only stock movement ledger."""

    class TransactionType(models.TextChoices):
        RECEIPT = "receipt", "Stock In"
        SALE = "sale", "Sale"
        RETURN = "return", "Return"
        ADJUSTMENT = "adjustment", "Adjustment"
        TRANSFER_IN = "transfer_in", "Transfer In"
        TRANSFER_OUT = "transfer_out", "Transfer Out"
        RESERVATION = "reservation", "Reservation"
        RELEASE = "release", "Release"

    movement_number = models.CharField(max_length=40, unique=True, db_index=True)
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.RESTRICT,
        related_name="transactions",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.RESTRICT,
        related_name="inventory_transactions",
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    transaction_type = models.CharField(max_length=30, choices=TransactionType.choices)
    quantity_change = models.IntegerField()
    quantity_after = models.IntegerField()
    unit_cost_cents = models.BigIntegerField(null=True, blank=True)
    sale_price_cents = models.BigIntegerField(null=True, blank=True)
    transfer_group_id = models.UUIDField(null=True, blank=True, db_index=True)
    reference_type = models.CharField(max_length=30, blank=True)
    reference_id = models.BigIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inventory_transactions",
    )

    class Meta:
        db_table = "inventory_transactions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["variant", "created_at"], name="idx_stock_mv_variant_dt"),
            models.Index(fields=["transaction_type", "created_at"], name="idx_stock_mv_type_dt"),
        ]

    @property
    def sku(self) -> str:
        return self.variant.sku


class StockMovement(InventoryTransaction):
    """ERP alias for stock movement ledger entries."""

    class Meta:
        proxy = True
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"


class InventoryAlert(PublicIdModel):
    """Persisted low-stock / out-of-stock notifications for staff."""

    class AlertType(models.TextChoices):
        LOW_STOCK = "low_stock", "Low Stock"
        OUT_OF_STOCK = "out_of_stock", "Out of Stock"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    inventory_level = models.ForeignKey(
        InventoryLevel,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    alert_type = models.CharField(max_length=20, choices=AlertType.choices)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    quantity_on_hand = models.IntegerField()
    reorder_point = models.IntegerField()
    shortfall = models.IntegerField(default=0)
    message = models.TextField(blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acknowledged_inventory_alerts",
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inventory_alerts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"], name="idx_inv_alert_status_dt"),
            models.Index(fields=["inventory_level", "status"], name="idx_inv_alert_level_st"),
        ]

    def __str__(self) -> str:
        return f"{self.alert_type} — {self.inventory_level.sku} @ {self.inventory_level.warehouse.code}"


def generate_movement_number(prefix: str) -> str:
    from django.utils import timezone

    stamp = timezone.now().strftime("%Y%m%d")
    token = uuid.uuid4().hex[:8].upper()
    return f"{prefix}-{stamp}-{token}"
