"""Inventory API serializers."""
from rest_framework import serializers

from apps.inventory.models import InventoryAlert, InventoryLevel, InventoryTransaction, Warehouse
from apps.inventory.services import InventoryService
from apps.inventory.valuation import InventoryValuationService
from apps.pricing.services import PricingService


class WarehouseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Warehouse
        fields = (
            "id",
            "public_id",
            "code",
            "name",
            "warehouse_type",
            "address_line1",
            "suburb",
            "state",
            "postcode",
            "is_active",
            "allows_pickup",
            "capacity_units",
        )
        read_only_fields = fields


class WarehouseAdminSerializer(WarehouseSerializer):
    sku_count = serializers.IntegerField(read_only=True, default=0)
    total_units = serializers.IntegerField(read_only=True, default=0)
    location = serializers.SerializerMethodField()

    class Meta(WarehouseSerializer.Meta):
        fields = WarehouseSerializer.Meta.fields + ("sku_count", "total_units", "location")

    def get_location(self, obj: Warehouse) -> str:
        parts = [obj.suburb, obj.state, obj.postcode]
        return ", ".join(p for p in parts if p) or obj.address_line1 or "—"


class WarehouseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            "code",
            "name",
            "warehouse_type",
            "address_line1",
            "suburb",
            "state",
            "postcode",
            "is_active",
            "allows_pickup",
            "capacity_units",
        )

    def validate_code(self, value: str) -> str:
        qs = Warehouse.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Warehouse code already exists.")
        return value


class InventorySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    sku = serializers.CharField(source="variant.sku", read_only=True)
    variant_id = serializers.UUIDField(source="variant.public_id", read_only=True)
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    quantity_available = serializers.IntegerField(read_only=True)
    cost_price_cents = serializers.IntegerField(source="average_cost_cents", read_only=True)
    sale_price_cents = serializers.IntegerField(source="last_sale_price_cents", read_only=True)
    valuation_ex_gst_cents = serializers.SerializerMethodField()
    valuation = serializers.SerializerMethodField()
    currency_code = serializers.SerializerMethodField()

    class Meta:
        model = InventoryLevel
        fields = (
            "id",
            "public_id",
            "sku",
            "variant_id",
            "product_name",
            "warehouse_code",
            "warehouse_name",
            "quantity_on_hand",
            "quantity_reserved",
            "quantity_available",
            "cost_price_cents",
            "sale_price_cents",
            "last_cost_cents",
            "reorder_point",
            "reorder_quantity",
            "valuation_ex_gst_cents",
            "valuation",
            "currency_code",
            "last_counted_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_valuation_ex_gst_cents(self, obj: InventoryLevel) -> int:
        return InventoryValuationService.line_valuation_ex_gst_cents(obj)

    def get_valuation(self, obj: InventoryLevel) -> dict:
        ex = InventoryValuationService.line_valuation_ex_gst_cents(obj)
        return InventoryValuationService.valuation_block(ex)

    def get_currency_code(self, obj: InventoryLevel) -> str:
        from django.conf import settings
        return settings.A2Z_CURRENCY_CODE


class StockMovementSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    sku = serializers.CharField(source="variant.sku", read_only=True)
    variant_id = serializers.UUIDField(source="variant.public_id", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    supplier_id = serializers.UUIDField(source="supplier.public_id", read_only=True, allow_null=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True, allow_null=True)
    quantity = serializers.SerializerMethodField()
    cost_price_cents = serializers.IntegerField(source="unit_cost_cents", read_only=True)
    value_ex_gst_cents = serializers.SerializerMethodField()
    valuation = serializers.SerializerMethodField()
    currency_code = serializers.SerializerMethodField()
    created_by_email = serializers.EmailField(source="created_by.email", read_only=True, allow_null=True)

    class Meta:
        model = InventoryTransaction
        fields = (
            "id",
            "public_id",
            "movement_number",
            "sku",
            "variant_id",
            "warehouse_code",
            "transaction_type",
            "quantity",
            "quantity_change",
            "quantity_after",
            "cost_price_cents",
            "value_ex_gst_cents",
            "valuation",
            "currency_code",
            "sale_price_cents",
            "supplier_id",
            "supplier_name",
            "transfer_group_id",
            "reference_type",
            "reference_id",
            "notes",
            "created_by_email",
            "created_at",
        )
        read_only_fields = fields

    def get_quantity(self, obj: InventoryTransaction) -> int:
        return abs(obj.quantity_change)

    def get_value_ex_gst_cents(self, obj: InventoryTransaction) -> int | None:
        if obj.unit_cost_cents is None:
            return None
        return abs(obj.quantity_change) * obj.unit_cost_cents

    def get_valuation(self, obj: InventoryTransaction) -> dict | None:
        ex = self.get_value_ex_gst_cents(obj)
        if ex is None:
            return None
        return InventoryValuationService.valuation_block(ex)

    def get_currency_code(self, obj: InventoryTransaction) -> str:
        from django.conf import settings
        return settings.A2Z_CURRENCY_CODE


class StockInSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=50)
    warehouse_code = serializers.CharField(max_length=10)
    quantity = serializers.IntegerField(min_value=1)
    cost_price_cents = serializers.IntegerField(min_value=0)
    sale_price_cents = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    reference_type = serializers.CharField(max_length=30, required=False, allow_blank=True)
    reference_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user = self.context["request"].user
        result = InventoryService.stock_in(
            sku=validated_data["sku"],
            warehouse_code=validated_data["warehouse_code"],
            quantity=validated_data["quantity"],
            unit_cost_cents=validated_data["cost_price_cents"],
            sale_price_cents=validated_data.get("sale_price_cents"),
            supplier_id=validated_data.get("supplier_id"),
            reference_type=validated_data.get("reference_type", ""),
            reference_id=validated_data.get("reference_id"),
            notes=validated_data.get("notes", ""),
            user=user,
        )
        return result


class StockOutSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=50)
    warehouse_code = serializers.CharField(max_length=10)
    quantity = serializers.IntegerField(min_value=1)
    cost_price_cents = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    sale_price_cents = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    reason = serializers.ChoiceField(
        choices=[
            ("sale", InventoryTransaction.TransactionType.SALE),
            ("adjustment", InventoryTransaction.TransactionType.ADJUSTMENT),
        ],
        default=InventoryTransaction.TransactionType.ADJUSTMENT,
    )
    reference_type = serializers.CharField(max_length=30, required=False, allow_blank=True)
    reference_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user = self.context["request"].user
        result = InventoryService.stock_out(
            sku=validated_data["sku"],
            warehouse_code=validated_data["warehouse_code"],
            quantity=validated_data["quantity"],
            sale_price_cents=validated_data.get("sale_price_cents"),
            unit_cost_cents=validated_data.get("cost_price_cents"),
            transaction_type=validated_data["reason"],
            reference_type=validated_data.get("reference_type", ""),
            reference_id=validated_data.get("reference_id"),
            notes=validated_data.get("notes", ""),
            user=user,
        )
        return result


class StockAdjustmentSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=50)
    warehouse_code = serializers.CharField(max_length=10)
    quantity_change = serializers.IntegerField()
    cost_price_cents = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_quantity_change(self, value: int) -> int:
        if value == 0:
            raise serializers.ValidationError("Quantity change must not be zero.")
        return value

    def validate(self, attrs):
        if attrs["quantity_change"] > 0 and attrs.get("cost_price_cents") is None:
            raise serializers.ValidationError(
                {"cost_price_cents": "Cost is required for positive adjustments."}
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        return InventoryService.stock_adjustment(
            sku=validated_data["sku"],
            warehouse_code=validated_data["warehouse_code"],
            quantity_change=validated_data["quantity_change"],
            unit_cost_cents=validated_data.get("cost_price_cents"),
            notes=validated_data.get("notes", ""),
            user=user,
        )


class StockTransferSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=50)
    from_warehouse_code = serializers.CharField(max_length=10)
    to_warehouse_code = serializers.CharField(max_length=10)
    quantity = serializers.IntegerField(min_value=1)
    sale_price_cents = serializers.IntegerField(min_value=0, required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user = self.context["request"].user
        result = InventoryService.stock_transfer(
            sku=validated_data["sku"],
            from_warehouse_code=validated_data["from_warehouse_code"],
            to_warehouse_code=validated_data["to_warehouse_code"],
            quantity=validated_data["quantity"],
            sale_price_cents=validated_data.get("sale_price_cents"),
            notes=validated_data.get("notes", ""),
            user=user,
        )
        return result


class StockOperationResponseSerializer(serializers.Serializer):
    movement = StockMovementSerializer()
    inventory = InventorySerializer()
    paired_movement = StockMovementSerializer(required=False, allow_null=True)


class InventoryLevelSerializer(InventorySerializer):
    """Backward-compatible alias used by legacy variant inventory endpoint."""

    pass


class LowStockAlertSerializer(InventorySerializer):
    alert_level = serializers.SerializerMethodField()
    shortfall = serializers.SerializerMethodField()

    class Meta(InventorySerializer.Meta):
        fields = InventorySerializer.Meta.fields + ("alert_level", "shortfall")
        read_only_fields = fields

    def get_alert_level(self, obj: InventoryLevel) -> str:
        if obj.quantity_on_hand <= 0:
            return "out_of_stock"
        if obj.quantity_on_hand <= obj.reorder_point:
            return "low_stock"
        return "ok"

    def get_shortfall(self, obj: InventoryLevel) -> int:
        return max(obj.reorder_point - obj.quantity_on_hand, 0)


class ReorderLevelSerializer(serializers.Serializer):
    reorder_point = serializers.IntegerField(min_value=0)
    reorder_quantity = serializers.IntegerField(min_value=0)

    def update(self, instance: InventoryLevel, validated_data):
        return InventoryService.update_reorder_levels(
            level=instance,
            reorder_point=validated_data["reorder_point"],
            reorder_quantity=validated_data["reorder_quantity"],
        )


class InventoryAlertSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    sku = serializers.CharField(source="inventory_level.variant.sku", read_only=True)
    product_name = serializers.CharField(
        source="inventory_level.variant.product.name", read_only=True
    )
    warehouse_code = serializers.CharField(
        source="inventory_level.warehouse.code", read_only=True
    )
    inventory_level_id = serializers.UUIDField(
        source="inventory_level.public_id", read_only=True
    )

    class Meta:
        model = InventoryAlert
        fields = (
            "id",
            "public_id",
            "sku",
            "product_name",
            "warehouse_code",
            "inventory_level_id",
            "alert_type",
            "status",
            "quantity_on_hand",
            "reorder_point",
            "shortfall",
            "message",
            "acknowledged_at",
            "created_at",
        )
        read_only_fields = fields


class TransferGroupSerializer(serializers.Serializer):
    transfer_group_id = serializers.UUIDField()
    sku = serializers.CharField()
    product_name = serializers.CharField()
    from_warehouse_code = serializers.CharField()
    to_warehouse_code = serializers.CharField(allow_null=True)
    quantity = serializers.IntegerField()
    notes = serializers.CharField(allow_blank=True)
    created_at = serializers.DateTimeField()
    created_by_email = serializers.EmailField(allow_null=True)


class ValuationSummarySerializer(serializers.Serializer):
    pass  # Built by service — returned as dict from view
