"""Configurable KPI engine — definitions and metric evaluation."""
from __future__ import annotations

from typing import Any

from django.db import transaction

from apps.analytics.constants import KpiCategory, KpiUnit
from apps.analytics.executive import (
    ExecutiveBiService,
    FinanceAnalyticsService,
    HrAnalyticsService,
    InventoryAnalyticsService,
    ProcurementAnalyticsService,
    SalesAnalyticsService,
)
from apps.analytics.models import KpiDefinition
from apps.core.exceptions import NotFoundError


DEFAULT_KPIS: tuple[dict[str, Any], ...] = (
    {"code": "revenue_30d", "name": "Revenue (30d)", "category": KpiCategory.EXECUTIVE, "metric_key": "revenueCents", "unit": KpiUnit.CURRENCY, "display_order": 1},
    {"code": "gross_margin", "name": "Gross Margin", "category": KpiCategory.EXECUTIVE, "metric_key": "grossMarginCents", "unit": KpiUnit.CURRENCY, "display_order": 2},
    {"code": "inventory_value", "name": "Inventory Value", "category": KpiCategory.EXECUTIVE, "metric_key": "inventoryValueCents", "unit": KpiUnit.CURRENCY, "display_order": 3},
    {"code": "open_orders", "name": "Open Orders", "category": KpiCategory.EXECUTIVE, "metric_key": "openOrders", "unit": KpiUnit.COUNT, "display_order": 4},
    {"code": "open_quotes", "name": "Open Quotes", "category": KpiCategory.EXECUTIVE, "metric_key": "openQuotes", "unit": KpiUnit.COUNT, "display_order": 5},
    {"code": "cash_position", "name": "Cash Position", "category": KpiCategory.EXECUTIVE, "metric_key": "cashPositionCents", "unit": KpiUnit.CURRENCY, "display_order": 6},
    {"code": "payroll_cost_ytd", "name": "Payroll Cost YTD", "category": KpiCategory.EXECUTIVE, "metric_key": "payrollCostYtdCents", "unit": KpiUnit.CURRENCY, "display_order": 7},
    {"code": "quote_conversion", "name": "Quote Conversion", "category": KpiCategory.SALES, "metric_key": "quoteConversionPct", "unit": KpiUnit.PERCENT, "display_order": 10},
    {"code": "inventory_turns", "name": "Inventory Turns", "category": KpiCategory.INVENTORY, "metric_key": "inventoryTurns", "unit": KpiUnit.COUNT, "display_order": 20},
    {"code": "headcount", "name": "Headcount", "category": KpiCategory.HR, "metric_key": "headcount", "unit": KpiUnit.COUNT, "display_order": 30},
)


class KpiEngineService:
    @classmethod
    @transaction.atomic
    def ensure_defaults(cls) -> None:
        for spec in DEFAULT_KPIS:
            KpiDefinition.objects.update_or_create(
                code=spec["code"],
                defaults={
                    "name": spec["name"],
                    "category": spec["category"],
                    "metric_key": spec["metric_key"],
                    "unit": spec["unit"],
                    "display_order": spec.get("display_order", 0),
                    "is_active": True,
                },
            )

    @staticmethod
    def list_definitions(*, category: str | None = None) -> list[KpiDefinition]:
        qs = KpiDefinition.objects.filter(is_active=True)
        if category:
            qs = qs.filter(category=category)
        return list(qs)

    @classmethod
    def evaluate_all(cls) -> list[dict]:
        cls.ensure_defaults()
        metrics = cls._load_metrics()
        results = []
        for kpi in cls.list_definitions():
            value = metrics.get(kpi.metric_key)
            if value is None and kpi.metric_key.endswith("Cents"):
                base_key = kpi.metric_key.replace("Cents", "Pct")
                value = metrics.get(base_key)
            results.append(
                {
                    "id": str(kpi.public_id),
                    "code": kpi.code,
                    "name": kpi.name,
                    "category": kpi.category,
                    "unit": kpi.unit,
                    "metricKey": kpi.metric_key,
                    "value": value,
                    "targetValue": float(kpi.target_value) if kpi.target_value is not None else None,
                    "onTarget": (
                        float(value) >= float(kpi.target_value)
                        if kpi.target_value is not None and value is not None
                        else None
                    ),
                }
            )
        return results

    @classmethod
    def _load_metrics(cls) -> dict[str, Any]:
        exec_kpis = ExecutiveBiService.get_snapshot()["executiveKpis"]
        inv = InventoryAnalyticsService.get_analytics()
        hr = HrAnalyticsService.get_analytics()
        sales = SalesAnalyticsService.get_analytics()
        return {
            **exec_kpis,
            "inventoryTurns": inv.get("inventoryTurns"),
            "quoteConversionPct": sales.get("quoteConversion", {}).get("conversionRatePct"),
            "headcount": hr.get("headcount"),
        }

    @staticmethod
    def get_definition(public_id) -> KpiDefinition:
        kpi = KpiDefinition.objects.filter(public_id=public_id).first()
        if not kpi:
            raise NotFoundError("KPI definition not found.")
        return kpi

    @classmethod
    @transaction.atomic
    def update_definition(cls, *, kpi: KpiDefinition, data: dict) -> KpiDefinition:
        if "targetValue" in data and data["targetValue"] is not None:
            kpi.target_value = data["targetValue"]
        if "isActive" in data:
            kpi.is_active = bool(data["isActive"])
        if "name" in data:
            kpi.name = data["name"]
        kpi.save()
        return kpi
