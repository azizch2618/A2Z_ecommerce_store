from rest_framework import serializers

from apps.trade_accounts.models import Quote, TradeAccount


class TradeAccountSerializer(serializers.ModelSerializer):
    credit_available_cents = serializers.IntegerField(read_only=True)

    class Meta:
        model = TradeAccount
        fields = (
            "public_id",
            "account_number",
            "tier",
            "status",
            "credit_limit_cents",
            "credit_used_cents",
            "credit_available_cents",
            "payment_terms_days",
        )
        read_only_fields = fields


class QuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quote
        fields = (
            "public_id",
            "quote_number",
            "status",
            "valid_until",
            "total_inc_gst_cents",
            "currency_code",
            "created_at",
        )
        read_only_fields = fields
