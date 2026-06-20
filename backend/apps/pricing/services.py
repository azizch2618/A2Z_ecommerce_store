from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings

from apps.core.exceptions import BusinessRuleError
from apps.pricing.models import Coupon


class PricingService:
    GST_RATE = Decimal(getattr(settings, "A2Z_GST_RATE", "0.1000"))

    @classmethod
    def calculate_gst(cls, amount_ex_gst_cents: int) -> int:
        return int(
            (Decimal(amount_ex_gst_cents) * cls.GST_RATE).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )

    @classmethod
    def price_block(cls, amount_ex_gst_cents: int, *, is_trade_price: bool = False) -> dict:
        gst_cents = cls.calculate_gst(amount_ex_gst_cents)
        return {
            "amount_ex_gst_cents": amount_ex_gst_cents,
            "gst_cents": gst_cents,
            "amount_inc_gst_cents": amount_ex_gst_cents + gst_cents,
            "gst_rate": float(cls.GST_RATE),
            "currency_code": settings.A2Z_CURRENCY_CODE,
            "compare_at_cents": None,
            "is_trade_price": is_trade_price,
        }

    @staticmethod
    def validate_coupon(code: str) -> Coupon:
        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        except Coupon.DoesNotExist as exc:
            raise BusinessRuleError("Invalid or expired coupon.") from exc
        return coupon
