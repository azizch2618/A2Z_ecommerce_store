"""Cart, wishlist, sales orders, payments, and shipments."""
from django.db import models

from apps.core.models import PublicIdModel


class Cart(PublicIdModel):
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
    )
    session_key = models.CharField(max_length=64, blank=True, db_index=True)
    currency_code = models.CharField(max_length=3, default="AUD")
    coupon_code = models.CharField(max_length=50, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "carts"


class CartItem(PublicIdModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.RESTRICT,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField()
    unit_price_cents = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = "cart_items"
        unique_together = [("cart", "variant")]


class Wishlist(PublicIdModel):
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        related_name="wishlists",
    )
    name = models.CharField(max_length=100, default="Default")
    is_default = models.BooleanField(default=True)

    class Meta:
        db_table = "wishlists"


class WishlistItem(PublicIdModel):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    desired_quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "wishlist_items"
        unique_together = [("wishlist", "variant")]


class Order(PublicIdModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        AWAITING_PAYMENT = "awaiting_payment", "Awaiting Payment"
        PAID = "paid", "Paid"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        PARTIAL = "partial", "Partial"
        REFUNDED = "refunded", "Refunded"
        FAILED = "failed", "Failed"

    order_number = models.CharField(max_length=20, unique=True, db_index=True)
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.RESTRICT,
        related_name="orders",
    )
    organization = models.ForeignKey(
        "customers.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    trade_account = models.ForeignKey(
        "trade_accounts.TradeAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    fulfilment_status = models.CharField(max_length=20, default="unfulfilled")
    currency_code = models.CharField(max_length=3, default="AUD")
    subtotal_ex_gst_cents = models.BigIntegerField(default=0)
    gst_total_cents = models.BigIntegerField(default=0)
    shipping_ex_gst_cents = models.BigIntegerField(default=0)
    shipping_gst_cents = models.BigIntegerField(default=0)
    discount_cents = models.BigIntegerField(default=0)
    total_inc_gst_cents = models.BigIntegerField(default=0)
    coupon = models.ForeignKey(
        "pricing.Coupon",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    guest_email = models.EmailField(blank=True, db_index=True)
    billing_address = models.JSONField(default=dict, blank=True)
    shipping_address = models.JSONField(default=dict, blank=True)
    shipping_method = models.JSONField(default=dict, blank=True)
    payment_method = models.CharField(max_length=30, blank=True)
    po_number = models.CharField(max_length=50, blank=True)
    customer_notes = models.TextField(blank=True)
    placed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    packed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "orders"
        ordering = ["-placed_at", "-created_at"]
        indexes = [
            models.Index(fields=["customer", "-placed_at"], name="idx_orders_customer_placed"),
            models.Index(fields=["status", "placed_at"], name="idx_orders_status_placed"),
        ]

    def __str__(self) -> str:
        return self.order_number


class OrderItem(PublicIdModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.RESTRICT,
        related_name="order_items",
    )
    sku = models.CharField(max_length=50, db_index=True)
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price_ex_gst_cents = models.BigIntegerField()
    unit_gst_cents = models.BigIntegerField()
    gst_rate = models.DecimalField(max_digits=5, decimal_places=4, default="0.1000")
    line_total_ex_gst_cents = models.BigIntegerField()
    line_gst_cents = models.BigIntegerField()
    line_total_inc_gst_cents = models.BigIntegerField()
    quantity_fulfilled = models.PositiveIntegerField(default=0)
    quantity_returned = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "order_items"

    @property
    def unit_price_inc_gst_cents(self) -> int:
        return int(self.unit_price_ex_gst_cents + self.unit_gst_cents)


class Payment(PublicIdModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        AUTHORIZED = "authorized", "Authorized"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        PARTIALLY_REFUNDED = "partially_refunded", "Partially Refunded"

    order = models.ForeignKey(Order, on_delete=models.RESTRICT, related_name="payments")
    payment_method = models.CharField(max_length=30)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )
    amount_cents = models.BigIntegerField()
    gst_cents = models.BigIntegerField(default=0)
    currency_code = models.CharField(max_length=3, default="AUD")
    gateway = models.CharField(max_length=30, default="stripe")
    gateway_payment_id = models.CharField(max_length=100, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=64, unique=True, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]


class Shipment(PublicIdModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="shipments")
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipments",
    )
    carrier = models.CharField(max_length=50, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True, db_index=True)
    tracking_url = models.URLField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "shipments"
        ordering = ["-created_at"]


class ShipmentItem(PublicIdModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="items")
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.RESTRICT,
        related_name="shipment_items",
    )
    quantity_shipped = models.PositiveIntegerField()

    class Meta:
        db_table = "shipment_items"
