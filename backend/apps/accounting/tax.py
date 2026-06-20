"""Australian GST tax engine — exclusive/inclusive calculations."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings

from apps.accounting.constants import TaxTreatment
from apps.pricing.services import PricingService


class TaxEngine:
    """GST calculations aligned with Australian BAS reporting (integer cents)."""

    GST_RATE = PricingService.GST_RATE

    @classmethod
    def gst_from_exclusive(cls, amount_ex_gst_cents: int) -> int:
        return PricingService.calculate_gst(amount_ex_gst_cents)

    @classmethod
    def split_inclusive(cls, amount_inc_gst_cents: int) -> tuple[int, int]:
        """Return (ex_gst_cents, gst_cents) from a GST-inclusive amount."""
        if amount_inc_gst_cents <= 0:
            return 0, 0
        divisor = Decimal("1") + cls.GST_RATE
        ex = int(
            (Decimal(amount_inc_gst_cents) / divisor).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )
        gst = amount_inc_gst_cents - ex
        return ex, gst

    @classmethod
    def to_inc_gst(cls, amount_ex_gst_cents: int) -> int:
        return amount_ex_gst_cents + cls.gst_from_exclusive(amount_ex_gst_cents)

    @classmethod
    def normalize(
        cls,
        *,
        amount_cents: int,
        treatment: str = TaxTreatment.GST_EXCLUSIVE,
    ) -> dict[str, int]:
        if treatment == TaxTreatment.GST_INCLUSIVE:
            ex, gst = cls.split_inclusive(amount_cents)
        elif treatment == TaxTreatment.GST_FREE:
            ex, gst = amount_cents, 0
        else:
            ex = amount_cents
            gst = cls.gst_from_exclusive(amount_cents)
        return {
            "amount_ex_gst_cents": ex,
            "gst_cents": gst,
            "amount_inc_gst_cents": ex + gst,
        }

    @classmethod
    def gst_rate_display(cls) -> float:
        return float(cls.GST_RATE)

    @classmethod
    def currency_code(cls) -> str:
        return getattr(settings, "A2Z_CURRENCY_CODE", "AUD")
