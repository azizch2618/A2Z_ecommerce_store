from rest_framework import serializers

from apps.suppliers.models import PurchaseOrder, PurchaseOrderLine, Supplier
from apps.suppliers.services import PurchaseOrderService


class SupplierSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    products_supplied = serializers.IntegerField(read_only=True, required=False, default=0)
    contact_person = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = (
            "id",
            "public_id",
            "code",
            "name",
            "abn",
            "email",
            "phone",
            "payment_terms_days",
            "is_active",
            "contact_details",
            "notes",
            "products_supplied",
            "contact_person",
            "status",
        )
        read_only_fields = fields

    def get_contact_person(self, obj: Supplier) -> str:
        contact = obj.contact_details or {}
        return contact.get("name", obj.email or "—")

    def get_status(self, obj: Supplier) -> str:
        return "active" if obj.is_active else "inactive"


class SupplierWriteSerializer(serializers.ModelSerializer):
    contact_person = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Supplier
        fields = (
            "code",
            "name",
            "abn",
            "email",
            "phone",
            "payment_terms_days",
            "is_active",
            "contact_details",
            "notes",
            "contact_person",
        )

    def validate_code(self, value: str) -> str:
        qs = Supplier.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Supplier code already exists.")
        return value

    def create(self, validated_data):
        contact_person = validated_data.pop("contact_person", "")
        contact_details = validated_data.get("contact_details") or {}
        if contact_person:
            contact_details["name"] = contact_person
        validated_data["contact_details"] = contact_details
        return Supplier.objects.create(**validated_data)

    def update(self, instance, validated_data):
        contact_person = validated_data.pop("contact_person", None)
        if contact_person is not None:
            contact_details = validated_data.get("contact_details", instance.contact_details or {})
            contact_details["name"] = contact_person
            validated_data["contact_details"] = contact_details
        return super().update(instance, validated_data)


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    sku = serializers.CharField(source="variant.sku", read_only=True)
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    quantity_remaining = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrderLine
        fields = (
            "id",
            "public_id",
            "sku",
            "product_name",
            "quantity_ordered",
            "quantity_received",
            "quantity_remaining",
            "unit_cost_cents",
        )
        read_only_fields = fields

    def get_quantity_remaining(self, obj: PurchaseOrderLine) -> int:
        return max(obj.quantity_ordered - obj.quantity_received, 0)


class PurchaseOrderSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    supplier_id = serializers.UUIDField(source="supplier.public_id", read_only=True)
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    warehouse_code = serializers.CharField(source="warehouse.code", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)
    lines = PurchaseOrderLineSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = (
            "id",
            "public_id",
            "po_number",
            "supplier_id",
            "supplier_name",
            "warehouse_code",
            "warehouse_name",
            "status",
            "total_ex_gst_cents",
            "expected_at",
            "lines",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class PurchaseOrderLineInputSerializer(serializers.Serializer):
    sku = serializers.CharField(max_length=50)
    quantity = serializers.IntegerField(min_value=1)
    unit_cost_cents = serializers.IntegerField(min_value=0)


class CreatePurchaseOrderSerializer(serializers.Serializer):
    supplier_id = serializers.UUIDField()
    warehouse_code = serializers.CharField(max_length=10)
    expected_at = serializers.DateTimeField(required=False, allow_null=True)
    lines = PurchaseOrderLineInputSerializer(many=True)

    def create(self, validated_data):
        user = self.context["request"].user
        return PurchaseOrderService.create(
            supplier_id=validated_data["supplier_id"],
            warehouse_code=validated_data["warehouse_code"],
            lines=validated_data["lines"],
            expected_at=validated_data.get("expected_at"),
            user=user,
        )


class ReceivePurchaseOrderLineSerializer(serializers.Serializer):
    line_id = serializers.UUIDField(required=False)
    sku = serializers.CharField(max_length=50, required=False)
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        if not attrs.get("line_id") and not attrs.get("sku"):
            raise serializers.ValidationError("Provide line_id or sku.")
        return attrs


class ReceivePurchaseOrderSerializer(serializers.Serializer):
    receipts = ReceivePurchaseOrderLineSerializer(many=True)

    def save(self, po: PurchaseOrder):
        user = self.context["request"].user
        return PurchaseOrderService.receive(
            po=po,
            receipts=self.validated_data["receipts"],
            user=user,
        )
