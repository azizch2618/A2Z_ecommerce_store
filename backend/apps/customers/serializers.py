"""Customer serializers."""
from rest_framework import serializers

from apps.customers.models import Address, Customer, Organization


class OrganizationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Organization
        fields = (
            "id",
            "public_id",
            "legal_name",
            "trading_name",
            "abn",
            "abn_verified",
        )
        read_only_fields = fields


class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Customer
        fields = (
            "id",
            "public_id",
            "customer_type",
            "trade_account_status",
            "credit_limit_cents",
            "payment_terms_days",
        )
        read_only_fields = fields


class AddressSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="public_id", read_only=True)

    class Meta:
        model = Address
        fields = (
            "id",
            "public_id",
            "label",
            "line1",
            "line2",
            "suburb",
            "state",
            "postcode",
            "country",
            "is_default_billing",
            "is_default_shipping",
        )
        read_only_fields = ("public_id",)
