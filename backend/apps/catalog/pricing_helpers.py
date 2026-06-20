"""Pricing and stock helpers for catalog API responses."""
from decimal import Decimal

from django.conf import settings
from django.db.models import F, Sum

from apps.catalog.models import ProductVariant
from apps.core.cache_utils import CACHE_TTL_PRICE_LIST, cache_get_or_set
from apps.pricing.models import PriceList, PriceListItem

GST_RATE = Decimal(getattr(settings, "A2Z_GST_RATE", "0.1000"))

_RETAIL_PRICE_LIST_CACHE_KEY = "a2z:price_list:retail"


def get_retail_price_list() -> PriceList | None:
    def _load() -> PriceList | None:
        return (
            PriceList.objects.filter(slug="retail", is_active=True).first()
            or PriceList.objects.filter(organization__isnull=True, is_active=True)
            .order_by("created_at")
            .first()
        )

    return cache_get_or_set(
        _RETAIL_PRICE_LIST_CACHE_KEY,
        _load,
        timeout=CACHE_TTL_PRICE_LIST,
    )


def build_price_block(
    unit_price_ex_gst_cents: int,
    *,
    is_trade_price: bool = False,
    compare_at_cents: int | None = None,
) -> dict:
    ex_gst = max(int(unit_price_ex_gst_cents), 0)
    gst_cents = int(Decimal(ex_gst) * GST_RATE)
    return {
        "amount_ex_gst_cents": ex_gst,
        "gst_cents": gst_cents,
        "amount_inc_gst_cents": ex_gst + gst_cents,
        "gst_rate": str(GST_RATE),
        "currency_code": getattr(settings, "A2Z_CURRENCY_CODE", "AUD"),
        "compare_at_cents": compare_at_cents,
        "is_trade_price": is_trade_price,
    }


def get_variant_unit_price_cents(
    variant: ProductVariant,
    price_list: PriceList | None = None,
) -> int:
    price_list = price_list or get_retail_price_list()
    if not price_list:
        return 0

    cached_items = getattr(variant, "_prefetched_price_items", None)
    if cached_items is not None:
        for item in cached_items:
            if item.price_list_id == price_list.pk:
                return int(item.unit_price_ex_gst_cents)
        return 0

    item = (
        PriceListItem.objects.filter(price_list=price_list, variant=variant)
        .order_by("min_quantity")
        .first()
    )
    return int(item.unit_price_ex_gst_cents) if item else 0


def build_stock_block(variant: ProductVariant) -> dict:
    levels = getattr(variant, "_prefetched_inventory_levels", None)
    if levels is None:
        levels = list(variant.inventory_levels.all())

    quantity_available = sum(
        max(level.quantity_on_hand - level.quantity_reserved, 0) for level in levels
    )

    if quantity_available > 10:
        status = "in_stock"
    elif quantity_available > 0:
        status = "low_stock"
    else:
        status = "out_of_stock"

    return {
        "status": status,
        "quantity_available": quantity_available,
        "lead_time_days": None,
    }


def aggregate_variant_stock(variant_ids: list[int]) -> dict[int, int]:
    if not variant_ids:
        return {}

    from apps.inventory.models import InventoryLevel

    rows = (
        InventoryLevel.objects.filter(variant_id__in=variant_ids)
        .values("variant_id")
        .annotate(
            available=Sum(F("quantity_on_hand") - F("quantity_reserved")),
        )
    )
    return {
        row["variant_id"]: max(int(row["available"] or 0), 0)
        for row in rows
    }
