from rest_framework import serializers

from apps.pricing.models import Coupon, PriceList


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ("code", "description", "discount_type", "discount_value")
        read_only_fields = fields


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = ("public_id", "name", "slug", "currency_code")
        read_only_fields = fields
