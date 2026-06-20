"""Pricing, GST, and promotion models."""
from decimal import Decimal

from django.db import models

from apps.core.models import PublicIdModel


class TaxRate(PublicIdModel):
    code = models.CharField(max_length=10, unique=True, default="GST")
    rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.1000"))
    country = models.CharField(max_length=2, default="AU")
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "tax_rates"


class PriceList(PublicIdModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    organization = models.ForeignKey(
        "customers.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="price_lists",
    )
    currency_code = models.CharField(max_length=3, default="AUD")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "price_lists"


class PriceListItem(PublicIdModel):
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.CASCADE, related_name="price_list_items")
    unit_price_ex_gst_cents = models.BigIntegerField()
    min_quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "price_list_items"
        unique_together = [("price_list", "variant", "min_quantity")]
        indexes = [
            models.Index(
                fields=["price_list", "unit_price_ex_gst_cents"],
                name="idx_price_list_items_price",
            ),
        ]


class Coupon(PublicIdModel):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FIXED_AMOUNT = "fixed_amount", "Fixed Amount"
        FREE_SHIPPING = "free_shipping", "Free Shipping"

    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.PositiveIntegerField()
    min_order_cents = models.BigIntegerField(default=0)
    max_discount_cents = models.BigIntegerField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    starts_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "coupons"
