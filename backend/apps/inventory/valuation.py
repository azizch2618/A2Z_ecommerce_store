"""Inventory valuation — weighted average cost, ex-GST (Australian BAS reporting)."""

from __future__ import annotations

from django.conf import settings
from django.db.models import Count, F, Sum

from apps.inventory.models import InventoryLevel, Warehouse
from apps.pricing.services import PricingService


class InventoryValuationService:
    @staticmethod
    def line_valuation_ex_gst_cents(level: InventoryLevel) -> int:
        return level.quantity_on_hand * level.average_cost_cents

    @staticmethod
    def valuation_block(ex_gst_cents: int) -> dict:
        gst_cents = PricingService.calculate_gst(ex_gst_cents)
        return {
            "amount_ex_gst_cents": ex_gst_cents,
            "gst_cents": gst_cents,
            "amount_inc_gst_cents": ex_gst_cents + gst_cents,
            "gst_rate": float(PricingService.GST_RATE),
            "currency_code": settings.A2Z_CURRENCY_CODE,
        }

    @classmethod
    def get_summary(cls, *, warehouse_code: str | None = None) -> dict:
        qs = InventoryLevel.objects.select_related("warehouse", "variant")
        if warehouse_code:
            qs = qs.filter(warehouse__code__iexact=warehouse_code)

        rows = qs.annotate(
            line_value_ex_gst=F("quantity_on_hand") * F("average_cost_cents"),
        )

        totals = rows.aggregate(
            sku_count=Count("id"),
            total_units=Sum("quantity_on_hand"),
            total_ex_gst_cents=Sum("line_value_ex_gst"),
        )

        total_ex = int(totals["total_ex_gst_cents"] or 0)
        by_warehouse: list[dict] = []

        if not warehouse_code:
            warehouse_totals = (
                rows.values("warehouse__code", "warehouse__name")
                .annotate(
                    sku_count=Count("id"),
                    total_units=Sum("quantity_on_hand"),
                    total_ex_gst_cents=Sum("line_value_ex_gst"),
                )
                .order_by("warehouse__code")
            )
            for wh in warehouse_totals:
                wh_ex = int(wh["total_ex_gst_cents"] or 0)
                by_warehouse.append(
                    {
                        "warehouse_code": wh["warehouse__code"],
                        "warehouse_name": wh["warehouse__name"],
                        "sku_count": wh["sku_count"],
                        "total_units": int(wh["total_units"] or 0),
                        **cls.valuation_block(wh_ex),
                    }
                )

        low_stock_value_ex = int(
            rows.filter(reorder_point__gt=0)
            .filter(quantity_on_hand__lte=F("reorder_point"))
            .aggregate(v=Sum("line_value_ex_gst"))["v"]
            or 0
        )

        return {
            "as_at": rows.order_by("-updated_at").values_list("updated_at", flat=True).first(),
            "warehouse_code": warehouse_code,
            "sku_count": totals["sku_count"] or 0,
            "total_units": int(totals["total_units"] or 0),
            **cls.valuation_block(total_ex),
            "low_stock_value": cls.valuation_block(low_stock_value_ex),
            "by_warehouse": by_warehouse,
            "valuation_method": "weighted_average_cost_ex_gst",
            "tax_note": (
                "Inventory is valued at weighted average cost excluding GST, "
                "consistent with Australian tax accounting (GST Act 1999)."
            ),
        }

    @classmethod
    def get_top_skus_by_value(
        cls,
        *,
        warehouse_code: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        qs = InventoryLevel.objects.select_related("warehouse", "variant", "variant__product")
        if warehouse_code:
            qs = qs.filter(warehouse__code__iexact=warehouse_code)

        top = (
            qs.annotate(line_value_ex_gst=F("quantity_on_hand") * F("average_cost_cents"))
            .filter(quantity_on_hand__gt=0)
            .order_by("-line_value_ex_gst")[:limit]
        )

        return [
            {
                "sku": level.variant.sku,
                "product_name": level.variant.product.name,
                "warehouse_code": level.warehouse.code,
                "quantity_on_hand": level.quantity_on_hand,
                "average_cost_cents": level.average_cost_cents,
                **cls.valuation_block(cls.line_valuation_ex_gst_cents(level)),
            }
            for level in top
        ]
