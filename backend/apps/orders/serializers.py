from rest_framework import serializers

from apps.catalog.pricing_helpers import (
    build_price_block,
    build_stock_block,
    get_variant_unit_price_cents,
)
from apps.orders.models import Cart, CartItem, Order, OrderItem, Payment, Shipment, Wishlist, WishlistItem
from apps.orders.services import CartService, WishlistService


class CartItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    variant_id = serializers.UUIDField(source="variant.public_id", read_only=True)
    sku = serializers.CharField(source="variant.sku", read_only=True)
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    variant_name = serializers.CharField(source="variant.name", read_only=True)
    image_url = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    line_total = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = (
            "id",
            "public_id",
            "variant_id",
            "sku",
            "product_name",
            "variant_name",
            "image_url",
            "quantity",
            "price",
            "line_total",
            "stock",
        )
        read_only_fields = fields

    def get_image_url(self, obj: CartItem) -> str | None:
        product = obj.variant.product
        primary = product.images.filter(is_primary=True).first()
        if primary:
            return primary.url
        first = product.images.order_by("sort_order").first()
        return first.url if first else None

    def get_price(self, obj: CartItem) -> dict:
        unit_ex = obj.unit_price_cents or get_variant_unit_price_cents(obj.variant)
        return build_price_block(int(unit_ex))

    def get_line_total(self, obj: CartItem) -> dict:
        price = self.get_price(obj)
        qty = obj.quantity
        ex = price["amount_ex_gst_cents"] * qty
        gst = price["gst_cents"] * qty
        return {
            "amount_ex_gst_cents": ex,
            "gst_cents": gst,
            "amount_inc_gst_cents": ex + gst,
        }

    def get_stock(self, obj: CartItem) -> dict:
        return build_stock_block(obj.variant)


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    totals = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = (
            "id",
            "public_id",
            "items",
            "item_count",
            "totals",
            "coupon",
            "currency_code",
            "updated_at",
        )
        read_only_fields = fields

    def get_item_count(self, obj: Cart) -> int:
        return obj.items.count()

    def get_totals(self, obj: Cart) -> dict:
        return CartService.build_cart_totals(obj)

    def get_coupon(self, obj: Cart) -> dict | None:
        if not obj.coupon_code:
            return None
        return {"code": obj.coupon_code, "description": None, "discount_cents": 0}


class AddToCartSerializer(serializers.Serializer):
    variant_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)


class MergeCartSerializer(serializers.Serializer):
    session_key = serializers.CharField(max_length=64)


class WishlistItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    variant_id = serializers.UUIDField(source="variant.public_id", read_only=True)
    product_id = serializers.UUIDField(source="variant.product.public_id", read_only=True)
    product_slug = serializers.CharField(source="variant.product.slug", read_only=True)
    sku = serializers.CharField(source="variant.sku", read_only=True)
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    variant_name = serializers.CharField(source="variant.name", read_only=True)
    brand = serializers.CharField(source="variant.product.brand.name", read_only=True)
    image_url = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()

    class Meta:
        model = WishlistItem
        fields = (
            "id",
            "variant_id",
            "product_id",
            "product_slug",
            "sku",
            "product_name",
            "variant_name",
            "brand",
            "image_url",
            "desired_quantity",
            "price",
            "stock",
        )
        read_only_fields = fields

    def get_image_url(self, obj: WishlistItem) -> str | None:
        images = list(obj.variant.product.images.all())
        if not images:
            return None
        image = next((img for img in images if img.is_primary), images[0])
        return image.url

    def get_price(self, obj: WishlistItem) -> dict:
        cents = get_variant_unit_price_cents(obj.variant)
        return build_price_block(cents)

    def get_stock(self, obj: WishlistItem) -> dict:
        return build_stock_block(obj.variant)


class WishlistSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    items = WishlistItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ("id", "items", "item_count", "updated_at")
        read_only_fields = fields

    def get_item_count(self, obj: Wishlist) -> int:
        return obj.items.count()


class AddToWishlistSerializer(serializers.Serializer):
    variant_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1, required=False)


class OrderLineItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "sku",
            "product_name",
            "variant_name",
            "quantity",
            "unit_price_ex_gst_cents",
            "unit_gst_cents",
            "gst_rate",
            "line_total_inc_gst_cents",
        )
        read_only_fields = fields


class OrderTotalsSerializer(serializers.Serializer):
    subtotal_ex_gst_cents = serializers.IntegerField()
    gst_total_cents = serializers.IntegerField()
    shipping_ex_gst_cents = serializers.IntegerField()
    shipping_gst_cents = serializers.IntegerField()
    discount_cents = serializers.IntegerField()
    total_inc_gst_cents = serializers.IntegerField()
    currency_code = serializers.CharField()


class ShipmentSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Shipment
        fields = (
            "id",
            "carrier",
            "tracking_number",
            "tracking_url",
            "status",
            "shipped_at",
            "delivered_at",
        )
        read_only_fields = fields


class PaymentSummarySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    client_secret = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ("id", "status", "amount_cents", "currency_code", "client_secret")
        read_only_fields = fields

    def get_client_secret(self, obj: Payment) -> str | None:
        return obj.gateway_response.get("client_secret")


class OrderSummarySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)
    item_count = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "order_number",
            "status",
            "payment_status",
            "item_count",
            "total_inc_gst_cents",
            "currency_code",
            "placed_at",
            "customer_name",
            "customer_email",
        )
        read_only_fields = fields

    def get_item_count(self, obj: Order) -> int:
        if hasattr(obj, "item_count"):
            return obj.item_count
        return obj.items.count()

    def get_customer_name(self, obj: Order) -> str:
        if not obj.customer.user_id:
            return "Guest"
        profile = getattr(obj.customer.user, "profile", None)
        if profile and (profile.first_name or profile.last_name):
            return f"{profile.first_name} {profile.last_name}".strip()
        return obj.customer.user.email

    def get_customer_email(self, obj: Order) -> str:
        if obj.customer.user_id:
            return obj.customer.user.email
        return obj.guest_email or ""


class OrderDetailSerializer(OrderSummarySerializer):
    items = OrderLineItemSerializer(many=True, read_only=True)
    totals = serializers.SerializerMethodField()
    billing_address = serializers.JSONField(read_only=True)
    shipping_address = serializers.JSONField(read_only=True)
    shipping_method = serializers.JSONField(read_only=True)
    payment = serializers.SerializerMethodField()
    shipments = ShipmentSerializer(many=True, read_only=True)

    class Meta(OrderSummarySerializer.Meta):
        fields = OrderSummarySerializer.Meta.fields + (
            "items",
            "totals",
            "billing_address",
            "shipping_address",
            "shipping_method",
            "payment",
            "shipments",
            "po_number",
            "customer_notes",
        )

    def get_totals(self, obj: Order) -> dict:
        from apps.orders.services import OrderService

        return OrderService.build_totals(obj)

    def get_payment(self, obj: Order) -> dict | None:
        payment = obj.payments.order_by("-created_at").first()
        if not payment:
            return None
        return PaymentSummarySerializer(payment).data


class OrderTrackSerializer(OrderSummarySerializer):
    shipments = ShipmentSerializer(many=True, read_only=True)

    class Meta(OrderSummarySerializer.Meta):
        fields = OrderSummarySerializer.Meta.fields + ("shipments",)


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    billing_address = serializers.JSONField()
    shipping_address = serializers.JSONField(required=False)
    shipping_method_id = serializers.UUIDField()
    payment_method = serializers.ChoiceField(
        choices=["card", "paypal", "bank_transfer", "trade_credit"],
    )
    email = serializers.EmailField(required=False)
    po_number = serializers.CharField(required=False, allow_blank=True, default="")
    customer_notes = serializers.CharField(required=False, allow_blank=True, default="")


class TrackOrderSerializer(serializers.Serializer):
    order_number = serializers.CharField(max_length=20)
    email = serializers.EmailField()


class OrderShipSerializer(serializers.Serializer):
    carrier = serializers.CharField(required=False, allow_blank=True, default="")
    tracking_number = serializers.CharField(required=False, allow_blank=True, default="")
    tracking_url = serializers.URLField(required=False, allow_blank=True, default="")


class OrderCancelSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="")


# Backward-compatible alias
OrderSerializer = OrderDetailSerializer
OrderItemSerializer = OrderLineItemSerializer
