"""Business report catalog and CSV export."""
from __future__ import annotations

import csv
import io
from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from apps.core.audit import log_operation
from apps.core.models import OperationalAuditLog
from apps.customers.models import Customer
from apps.inventory.models import InventoryLevel
from apps.orders.models import Order, OrderItem

REPORT_CATALOG = [
    {
        "id": "sales",
        "name": "Sales Report",
        "description": "Revenue and order volume by period (paid orders).",
    },
    {
        "id": "inventory",
        "name": "Inventory Report",
        "description": "Stock positions, valuation, and low-stock SKUs by warehouse.",
    },
    {
        "id": "gst",
        "name": "GST Report",
        "description": "GST collected on sales orders for BAS reporting.",
    },
    {
        "id": "customers",
        "name": "Customer Report",
        "description": "Customer acquisition, trade status, and order counts.",
    },
]


def list_reports() -> list[dict]:
    return REPORT_CATALOG


def _date_range(days: int = 30):
    end = timezone.now()
    start = end - timedelta(days=days)
    return start, end


def export_report_csv(*, report_id: str, user) -> tuple[str, str]:
    """Return (filename, csv_content)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    if report_id == "sales":
        start, end = _date_range(90)
        writer.writerow(["order_number", "status", "placed_at", "total_inc_gst_cents", "gst_total_cents"])
        for order in Order.objects.filter(placed_at__gte=start, placed_at__lte=end).order_by("-placed_at"):
            writer.writerow([
                order.order_number,
                order.status,
                order.placed_at.isoformat() if order.placed_at else "",
                order.total_inc_gst_cents,
                order.gst_total_cents,
            ])
        filename = "sales-report.csv"

    elif report_id == "inventory":
        writer.writerow(["warehouse", "sku", "product", "qty_on_hand", "avg_cost_cents", "valuation_ex_gst"])
        for row in InventoryLevel.objects.select_related("warehouse", "variant__product").order_by("warehouse__code"):
            valuation = row.average_cost_cents * max(row.quantity_on_hand, 0)
            writer.writerow([
                row.warehouse.code,
                row.variant.sku,
                row.variant.product.name,
                row.quantity_on_hand,
                row.average_cost_cents,
                valuation,
            ])
        filename = "inventory-report.csv"

    elif report_id == "gst":
        start, end = _date_range(90)
        writer.writerow(["order_number", "placed_at", "subtotal_ex_gst", "gst_total", "total_inc_gst"])
        paid_statuses = [Order.Status.PAID, Order.Status.PACKED, Order.Status.SHIPPED, Order.Status.DELIVERED]
        for order in Order.objects.filter(
            status__in=paid_statuses,
            placed_at__gte=start,
            placed_at__lte=end,
        ).order_by("-placed_at"):
            writer.writerow([
                order.order_number,
                order.placed_at.isoformat() if order.placed_at else "",
                order.subtotal_ex_gst_cents,
                order.gst_total_cents,
                order.total_inc_gst_cents,
            ])
        filename = "gst-report.csv"

    elif report_id == "customers":
        writer.writerow(["email", "customer_type", "trade_status", "total_orders", "total_spent_cents", "joined_at"])
        for customer in Customer.objects.select_related("user").order_by("-created_at"):
            email = customer.user.email if customer.user_id else ""
            writer.writerow([
                email,
                customer.customer_type,
                customer.trade_account_status or "",
                customer.total_orders,
                customer.total_spent_cents,
                customer.created_at.isoformat(),
            ])
        filename = "customer-report.csv"

    else:
        raise ValueError(f"Unknown report: {report_id}")

    log_operation(
        user=user,
        module=OperationalAuditLog.Module.REPORTS,
        action="export",
        resource_type="report",
        resource_id=report_id,
        details={"format": "csv"},
    )
    return filename, buffer.getvalue()
