"""WMS — bin locations, transfers, picks, putaway, cycle counts, adjustments."""
from django.db import models

from apps.core.models import PublicIdModel
from apps.wms.constants import (
    AdjustmentStatus,
    BinType,
    CycleCountStatus,
    PickListStatus,
    PutawayStatus,
    TransferStatus,
    TransferType,
)


class WarehouseZone(PublicIdModel):
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        related_name="zones",
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "wms_zones"
        unique_together = [("warehouse", "code")]
        ordering = ["warehouse__code", "code"]

    def __str__(self) -> str:
        return f"{self.warehouse.code}/{self.code}"


class WarehouseAisle(PublicIdModel):
    zone = models.ForeignKey(
        WarehouseZone,
        on_delete=models.CASCADE,
        related_name="aisles",
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "wms_aisles"
        unique_together = [("zone", "code")]
        ordering = ["zone__code", "code"]

    @property
    def warehouse(self):
        return self.zone.warehouse

    def __str__(self) -> str:
        return f"{self.zone}/{self.code}"


class WarehouseBin(PublicIdModel):
    aisle = models.ForeignKey(
        WarehouseAisle,
        on_delete=models.CASCADE,
        related_name="bins",
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100, blank=True)
    bin_type = models.CharField(
        max_length=20,
        choices=BinType.choices,
        default=BinType.PICK,
    )
    is_active = models.BooleanField(default=True)
    max_units = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "wms_bins"
        unique_together = [("aisle", "code")]
        ordering = ["aisle__zone__code", "aisle__code", "code"]

    @property
    def warehouse(self):
        return self.aisle.zone.warehouse

    @property
    def location_code(self) -> str:
        z = self.aisle.zone
        return f"{z.warehouse.code}-{z.code}-{self.aisle.code}-{self.code}"

    def __str__(self) -> str:
        return self.location_code


class BinInventory(PublicIdModel):
    """Stock quantity at bin granularity."""

    bin = models.ForeignKey(
        WarehouseBin,
        on_delete=models.CASCADE,
        related_name="inventory",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.CASCADE,
        related_name="bin_inventory",
    )
    quantity_on_hand = models.IntegerField(default=0)

    class Meta:
        db_table = "wms_bin_inventory"
        unique_together = [("bin", "variant")]

    @property
    def sku(self) -> str:
        return self.variant.sku


class StockTransfer(PublicIdModel):
    transfer_number = models.CharField(max_length=30, unique=True)
    transfer_type = models.CharField(max_length=20, choices=TransferType.choices)
    status = models.CharField(
        max_length=20,
        choices=TransferStatus.choices,
        default=TransferStatus.DRAFT,
    )
    from_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.RESTRICT,
        related_name="transfers_out",
    )
    to_warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.RESTRICT,
        related_name="transfers_in",
    )
    from_bin = models.ForeignKey(
        WarehouseBin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_out",
    )
    to_bin = models.ForeignKey(
        WarehouseBin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_in",
    )
    requires_approval = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="stock_transfers_created",
    )

    class Meta:
        db_table = "wms_stock_transfers"
        ordering = ["-created_at"]


class StockTransferLine(PublicIdModel):
    transfer = models.ForeignKey(
        StockTransfer,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.RESTRICT,
        related_name="transfer_lines",
    )
    sku = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    quantity_moved = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "wms_stock_transfer_lines"


class PickList(PublicIdModel):
    pick_number = models.CharField(max_length=30, unique=True)
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.RESTRICT,
        related_name="pick_lists",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pick_lists",
    )
    status = models.CharField(
        max_length=20,
        choices=PickListStatus.choices,
        default=PickListStatus.DRAFT,
    )
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_pick_lists",
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="pick_lists_created",
    )

    class Meta:
        db_table = "wms_pick_lists"
        ordering = ["-created_at"]


class PickListLine(PublicIdModel):
    pick_list = models.ForeignKey(
        PickList,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.RESTRICT,
        related_name="pick_lines",
    )
    sku = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255, blank=True)
    quantity_required = models.PositiveIntegerField()
    quantity_picked = models.PositiveIntegerField(default=0)
    from_bin = models.ForeignKey(
        WarehouseBin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pick_lines",
    )

    class Meta:
        db_table = "wms_pick_list_lines"


class PutawayTask(PublicIdModel):
    task_number = models.CharField(max_length=30, unique=True)
    goods_receipt = models.ForeignKey(
        "procurement.GoodsReceipt",
        on_delete=models.CASCADE,
        related_name="putaway_tasks",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.RESTRICT,
        related_name="putaway_tasks",
    )
    status = models.CharField(
        max_length=20,
        choices=PutawayStatus.choices,
        default=PutawayStatus.PENDING,
    )
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="putaway_tasks",
    )

    class Meta:
        db_table = "wms_putaway_tasks"
        ordering = ["-created_at"]


class PutawayTaskLine(PublicIdModel):
    task = models.ForeignKey(
        PutawayTask,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.RESTRICT,
        related_name="putaway_lines",
    )
    sku = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    quantity_putaway = models.PositiveIntegerField(default=0)
    target_bin = models.ForeignKey(
        WarehouseBin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="putaway_lines",
    )

    class Meta:
        db_table = "wms_putaway_task_lines"


class CycleCount(PublicIdModel):
    count_number = models.CharField(max_length=30, unique=True)
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.RESTRICT,
        related_name="cycle_counts",
    )
    status = models.CharField(
        max_length=20,
        choices=CycleCountStatus.choices,
        default=CycleCountStatus.DRAFT,
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="cycle_counts_created",
    )

    class Meta:
        db_table = "wms_cycle_counts"
        ordering = ["-created_at"]


class CycleCountLine(PublicIdModel):
    cycle_count = models.ForeignKey(
        CycleCount,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.RESTRICT,
        related_name="cycle_count_lines",
    )
    sku = models.CharField(max_length=50)
    bin = models.ForeignKey(
        WarehouseBin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cycle_count_lines",
    )
    expected_qty = models.IntegerField(default=0)
    counted_qty = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "wms_cycle_count_lines"

    @property
    def variance(self) -> int | None:
        if self.counted_qty is None:
            return None
        return self.counted_qty - self.expected_qty


class InventoryAdjustmentRequest(PublicIdModel):
    adjustment_number = models.CharField(max_length=30, unique=True)
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.RESTRICT,
        related_name="adjustment_requests",
    )
    status = models.CharField(
        max_length=20,
        choices=AdjustmentStatus.choices,
        default=AdjustmentStatus.DRAFT,
    )
    reason = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="adjustment_requests_created",
    )

    class Meta:
        db_table = "wms_adjustment_requests"
        ordering = ["-created_at"]


class InventoryAdjustmentLine(PublicIdModel):
    request = models.ForeignKey(
        InventoryAdjustmentRequest,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.RESTRICT,
        related_name="adjustment_lines",
    )
    sku = models.CharField(max_length=50)
    bin = models.ForeignKey(
        WarehouseBin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="adjustment_lines",
    )
    quantity_change = models.IntegerField()
    unit_cost_cents = models.BigIntegerField(default=0)

    class Meta:
        db_table = "wms_adjustment_lines"
