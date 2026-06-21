"""Executive BI orchestration — cross-module KPI snapshot."""
from __future__ import annotations

from datetime import timedelta

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.accounting.constants import StandardAccountCode
from apps.accounting.services import ReportingService
from apps.analytics.dashboard import _inventory_value_cents
from apps.core.cache_utils import CACHE_TTL_DASHBOARD, cache_get_or_set
from apps.hrm.services import HrmDashboardService
from apps.orders.models import Order, OrderItem
from apps.payables.services import PayablesReportingService
from apps.payroll.services import PayrollDashboardService
from apps.procurement.services import ProcurementDashboardService
from apps.quotes.services import QuoteService
from apps.receivables.services import ReceivablesReportingService
from apps.trade_accounts.models import Quote
from apps.wms.services import WmsDashboardService

_PAID = [
    Order.Status.PAID,
    Order.Status.PACKED,
    Order.Status.SHIPPED,
    Order.Status.DELIVERED,
]

_OPEN_ORDER = [
    Order.Status.PENDING,
    Order.Status.PAID,
    Order.Status.PACKED,
    Order.Status.SHIPPED,
]

_OPEN_QUOTE = [
    Quote.Status.DRAFT,
    Quote.Status.PENDING_APPROVAL,
    Quote.Status.SENT,
    Quote.Status.ACCEPTED,
]


class ExecutiveBiService:
    @classmethod
    def get_snapshot(cls) -> dict:
        return cache_get_or_set(
            "a2z:bi:executive",
            cls._build_snapshot,
            timeout=CACHE_TTL_DASHBOARD,
        )

    @classmethod
    def _build_snapshot(cls) -> dict:
        now = timezone.now()
        thirty_days = now - timedelta(days=30)

        revenue_cents = (
            Order.objects.filter(status__in=_PAID, placed_at__gte=thirty_days).aggregate(
                t=Sum("total_inc_gst_cents")
            )["t"]
            or 0
        )

        cogs_cents = 0
        from apps.inventory.models import InventoryLevel

        for item in OrderItem.objects.filter(
            order__status__in=_PAID,
            order__placed_at__gte=thirty_days,
        ).select_related("variant")[:2000]:
            level = InventoryLevel.objects.filter(variant=item.variant).first()
            cost = level.average_cost_cents if level else 0
            cogs_cents += cost * item.quantity

        gross_margin_cents = int(revenue_cents) - cogs_cents
        gross_margin_pct = round(gross_margin_cents / revenue_cents * 100, 1) if revenue_cents else 0.0

        inventory_value = _inventory_value_cents()
        open_orders = Order.objects.filter(status__in=_OPEN_ORDER).count()
        open_quotes = Quote.objects.filter(status__in=_OPEN_QUOTE).count()

        cash_cents = 0
        for row in ReportingService.trial_balance():
            if row["accountCode"] == StandardAccountCode.BANK:
                cash_cents = row["balanceCents"]
                break

        payroll = PayrollDashboardService.get_kpis()
        ar = ReceivablesReportingService.ar_summary()
        procurement = ProcurementDashboardService.get_dashboard_kpis()
        wms = WmsDashboardService.get_kpis()
        hrm = HrmDashboardService.get_kpis()
        quotes = QuoteService.get_dashboard_kpis()

        return {
            "generatedAt": now.isoformat(),
            "executiveKpis": {
                "revenueCents": int(revenue_cents),
                "grossMarginCents": gross_margin_cents,
                "grossMarginPct": gross_margin_pct,
                "inventoryValueCents": inventory_value,
                "openOrders": open_orders,
                "openQuotes": open_quotes,
                "cashPositionCents": cash_cents,
                "payrollCostYtdCents": payroll.get("totalPayrollYtdCents", 0),
                "arOutstandingCents": ar.get("totalOutstandingCents", 0),
                "procurementSpendCents": procurement.get("procurement_spend_cents", 0),
                "headcount": hrm.get("headcount", 0),
                "quoteConversionPct": quotes.get("conversion_rate", 0),
                "wmsInventoryValueCents": wms.get("inventory_value_cents", 0),
            },
        }


class SalesAnalyticsService:
    @staticmethod
    def get_analytics() -> dict:
        now = timezone.now()
        twelve_months = now - timedelta(days=365)

        revenue_by_month = []
        rows = (
            Order.objects.filter(status__in=_PAID, placed_at__gte=twelve_months)
            .annotate(month=TruncMonth("placed_at"))
            .values("month")
            .annotate(revenueCents=Sum("total_inc_gst_cents"), orderCount=Count("id"))
            .order_by("month")
        )
        for row in rows:
            revenue_by_month.append(
                {
                    "month": row["month"].strftime("%Y-%m"),
                    "label": row["month"].strftime("%b %Y"),
                    "revenueCents": int(row["revenueCents"] or 0),
                    "orderCount": row["orderCount"],
                }
            )

        revenue_by_customer = []
        cust_rows = (
            Order.objects.filter(status__in=_PAID)
            .values("customer__public_id", "customer__user__email")
            .annotate(revenueCents=Sum("total_inc_gst_cents"), orderCount=Count("id"))
            .order_by("-revenueCents")[:20]
        )
        for row in cust_rows:
            revenue_by_customer.append(
                {
                    "customerId": str(row["customer__public_id"]) if row["customer__public_id"] else None,
                    "customerName": row["customer__user__email"] or "Guest",
                    "revenueCents": int(row["revenueCents"] or 0),
                    "orderCount": row["orderCount"],
                }
            )

        revenue_by_product = []
        prod_rows = (
            OrderItem.objects.filter(order__status__in=_PAID)
            .values("sku", "product_name")
            .annotate(revenueCents=Sum("line_total_inc_gst_cents"), units=Sum("quantity"))
            .order_by("-revenueCents")[:20]
        )
        for row in prod_rows:
            revenue_by_product.append(
                {
                    "sku": row["sku"],
                    "productName": row["product_name"],
                    "revenueCents": int(row["revenueCents"] or 0),
                    "units": int(row["units"] or 0),
                }
            )

        quotes = QuoteService.get_dashboard_kpis()
        return {
            "revenueByMonth": revenue_by_month,
            "revenueByCustomer": revenue_by_customer,
            "revenueByProduct": revenue_by_product,
            "quoteConversion": {
                "draftQuotes": quotes.get("draft_quotes", 0),
                "pendingApproval": quotes.get("pending_approval", 0),
                "accepted": quotes.get("accepted", 0),
                "converted": quotes.get("converted", 0),
                "conversionRatePct": quotes.get("conversion_rate", 0),
            },
        }


class InventoryAnalyticsService:
    @staticmethod
    def get_analytics() -> dict:
        from apps.inventory.models import InventoryLevel, InventoryTransaction
        from apps.inventory.valuation import InventoryValuationService
        from apps.wms.models import BinInventory, WarehouseBin

        summary = InventoryValuationService.get_summary()
        total_value = int(summary.get("amount_ex_gst_cents", 0))

        ninety_days = timezone.now() - timedelta(days=90)
        moved_skus = set(
            InventoryTransaction.objects.filter(created_at__gte=ninety_days).values_list(
                "variant_id", flat=True
            )
        )

        dead_stock = []
        for level in (
            InventoryLevel.objects.filter(quantity_on_hand__gt=0)
            .select_related("variant__product", "warehouse")
            .order_by("-quantity_on_hand")[:500]
        ):
            if level.variant_id not in moved_skus:
                val = level.quantity_on_hand * level.average_cost_cents
                dead_stock.append(
                    {
                        "sku": level.variant.sku,
                        "productName": level.variant.product.name,
                        "warehouse": level.warehouse.code,
                        "quantity": level.quantity_on_hand,
                        "valueCents": val,
                    }
                )
        dead_stock.sort(key=lambda r: -r["valueCents"])
        dead_stock = dead_stock[:20]

        thirty_days = timezone.now() - timedelta(days=30)
        fast_moving = []
        fm_rows = (
            OrderItem.objects.filter(order__placed_at__gte=thirty_days, order__status__in=_PAID)
            .values("sku", "product_name")
            .annotate(units=Sum("quantity"))
            .order_by("-units")[:15]
        )
        for row in fm_rows:
            fast_moving.append(
                {
                    "sku": row["sku"],
                    "productName": row["product_name"],
                    "unitsSold": int(row["units"] or 0),
                }
            )

        total_bins = WarehouseBin.objects.filter(is_active=True).count()
        used_bins = (
            BinInventory.objects.filter(quantity_on_hand__gt=0).values("bin_id").distinct().count()
        )
        utilization_pct = round(used_bins / max(total_bins, 1) * 100, 1)

        cogs_90d = (
            OrderItem.objects.filter(
                order__placed_at__gte=ninety_days,
                order__status__in=_PAID,
            ).aggregate(t=Sum("line_total_ex_gst_cents"))["t"]
            or 0
        )
        turns = round(float(cogs_90d) / max(total_value, 1) * 4, 2) if total_value else 0.0

        return {
            "inventoryValueCents": total_value,
            "inventoryTurns": turns,
            "deadStock": dead_stock,
            "fastMovingProducts": fast_moving,
            "warehouseUtilization": {
                "totalBins": total_bins,
                "usedBins": used_bins,
                "utilizationPct": utilization_pct,
            },
            "byWarehouse": summary.get("by_warehouse", []),
        }


class ProcurementAnalyticsService:
    @staticmethod
    def get_analytics() -> dict:
        from apps.procurement.services import SupplierPerformanceService
        from apps.suppliers.models import PurchaseOrder, PurchaseOrderLine
        from apps.suppliers.models import Supplier

        spend_by_supplier = []
        sup_rows = (
            PurchaseOrder.objects.filter(
                status__in=[
                    PurchaseOrder.Status.CONFIRMED,
                    PurchaseOrder.Status.PARTIAL_RECEIVED,
                    PurchaseOrder.Status.RECEIVED,
                ]
            )
            .values("supplier__public_id", "supplier__name")
            .annotate(spendCents=Sum("total_ex_gst_cents"), orderCount=Count("id"))
            .order_by("-spendCents")[:15]
        )
        for row in sup_rows:
            spend_by_supplier.append(
                {
                    "supplierId": str(row["supplier__public_id"]),
                    "supplierName": row["supplier__name"],
                    "spendCents": int(row["spendCents"] or 0),
                    "orderCount": row["orderCount"],
                }
            )

        spend_by_category: dict[str, int] = {}
        for line in PurchaseOrderLine.objects.select_related(
            "variant__product", "purchase_order"
        ).filter(
            purchase_order__status__in=[
                PurchaseOrder.Status.CONFIRMED,
                PurchaseOrder.Status.PARTIAL_RECEIVED,
                PurchaseOrder.Status.RECEIVED,
            ]
        )[:2000]:
            cat = line.variant.product.categories.first()
            name = cat.name if cat else "Uncategorised"
            spend_by_category[name] = spend_by_category.get(name, 0) + (
                line.quantity_ordered * line.unit_cost_cents
            )

        spend_by_category_list = sorted(
            [{"category": k, "spendCents": v} for k, v in spend_by_category.items()],
            key=lambda r: -r["spendCents"],
        )[:15]

        supplier_performance = []
        for supplier in Supplier.objects.filter(is_active=True).order_by("name")[:10]:
            supplier_performance.append(SupplierPerformanceService.get_supplier_kpis(supplier))

        dashboard = ProcurementDashboardService.get_dashboard_kpis()
        return {
            "totalSpendCents": dashboard.get("procurement_spend_cents", 0),
            "openRequisitions": dashboard.get("open_requisitions", 0),
            "openPurchaseOrders": dashboard.get("open_purchase_orders", 0),
            "spendBySupplier": spend_by_supplier,
            "spendByCategory": spend_by_category_list,
            "supplierPerformance": supplier_performance,
            "aggregatePerformance": dashboard.get("supplier_performance", {}),
        }


class FinanceAnalyticsService:
    @staticmethod
    def get_analytics() -> dict:
        ar_aging = ReceivablesReportingService.customer_aging()
        ap_aging = PayablesReportingService.supplier_aging()
        ar_summary = ReceivablesReportingService.ar_summary()
        ap_summary = PayablesReportingService.ap_summary()

        trial = ReportingService.trial_balance()
        cash_cents = 0
        revenue_cents = 0
        expense_cents = 0
        for row in trial:
            if row["accountCode"] == StandardAccountCode.BANK:
                cash_cents = row["balanceCents"]
            if row["accountType"] == "revenue":
                revenue_cents += row["creditCents"] - row["debitCents"]
            if row["accountType"] == "expense":
                expense_cents += row["debitCents"] - row["creditCents"]

        ar_buckets = {
            "currentCents": sum(r["currentCents"] for r in ar_aging),
            "days31_60Cents": sum(r["days31_60Cents"] for r in ar_aging),
            "days61_90Cents": sum(r["days61_90Cents"] for r in ar_aging),
            "days91_120Cents": sum(r["days91_120Cents"] for r in ar_aging),
            "days120PlusCents": sum(r["days120PlusCents"] for r in ar_aging),
        }
        ap_buckets = {
            "currentCents": sum(r["currentCents"] for r in ap_aging),
            "days31_60Cents": sum(r["days31_60Cents"] for r in ap_aging),
            "days61_90Cents": sum(r["days61_90Cents"] for r in ap_aging),
            "days91_120Cents": sum(r["days91_120Cents"] for r in ap_aging),
            "days120PlusCents": sum(r["days120PlusCents"] for r in ap_aging),
        }

        return {
            "arAging": ar_buckets,
            "apAging": ap_buckets,
            "arSummary": ar_summary,
            "apSummary": ap_summary,
            "cashFlow": {
                "cashPositionCents": cash_cents,
                "arOutstandingCents": ar_summary.get("totalOutstandingCents", 0),
                "apOutstandingCents": ap_summary.get("totalOutstandingCents", 0),
                "netWorkingCapitalCents": ar_summary.get("totalOutstandingCents", 0)
                - ap_summary.get("totalOutstandingCents", 0),
            },
            "profitability": {
                "revenueCents": revenue_cents,
                "expenseCents": expense_cents,
                "netPositionCents": revenue_cents - expense_cents,
            },
            "topArCustomers": ar_aging[:10],
            "topApSuppliers": ap_aging[:10],
        }


class HrAnalyticsService:
    @staticmethod
    def get_analytics() -> dict:
        from apps.hrm.constants import LeaveRequestStatus
        from apps.hrm.models import LeaveRequest

        hrm = HrmDashboardService.get_kpis()
        payroll = PayrollDashboardService.get_kpis()

        six_months = timezone.now() - timedelta(days=180)
        leave_trends = []
        rows = (
            LeaveRequest.objects.filter(
                status=LeaveRequestStatus.APPROVED,
                start_date__gte=six_months.date(),
            )
            .annotate(month=TruncMonth("start_date"))
            .values("month", "leave_type")
            .annotate(totalDays=Sum("days"), requestCount=Count("id"))
            .order_by("month")
        )
        by_month: dict[str, dict] = {}
        for row in rows:
            key = row["month"].strftime("%Y-%m")
            if key not in by_month:
                by_month[key] = {"month": key, "label": row["month"].strftime("%b %Y"), "byType": {}}
            by_month[key]["byType"][row["leave_type"]] = {
                "totalDays": float(row["totalDays"] or 0),
                "requestCount": row["requestCount"],
            }
        leave_trends = list(by_month.values())

        return {
            "headcount": hrm.get("headcount", 0),
            "onLeaveToday": hrm.get("onLeaveToday", 0),
            "pendingLeaveRequests": hrm.get("pendingLeaveRequests", 0),
            "leaveTrends": leave_trends,
            "payrollCostByDepartment": payroll.get("departmentCosts", []),
            "payrollYtdCents": payroll.get("totalPayrollYtdCents", 0),
            "payrollGrossYtdCents": payroll.get("totalGrossYtdCents", 0),
        }
