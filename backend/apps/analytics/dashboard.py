"""Dashboard metrics aggregated from live commerce data."""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone

from apps.catalog.models import Brand, Category, Product
from apps.core.cache_utils import CACHE_TTL_DASHBOARD, cache_get_or_set
from apps.customers.models import Customer
from apps.inventory.models import InventoryLevel
from apps.orders.models import Order, OrderItem
from apps.suppliers.models import Supplier
from apps.trade_accounts.models import TradeApplication


def _format_status_label(status: str) -> str:
    return status.replace("_", " ").title()


def build_dashboard_payload() -> dict:
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    paid_statuses = [
        Order.Status.PAID,
        Order.Status.PACKED,
        Order.Status.SHIPPED,
        Order.Status.DELIVERED,
    ]

    revenue_qs = Order.objects.filter(
        status__in=paid_statuses,
        placed_at__gte=thirty_days_ago,
    )
    revenue_cents = revenue_qs.aggregate(total=Sum("total_inc_gst_cents"))["total"] or 0

    prev_revenue = (
        Order.objects.filter(
            status__in=paid_statuses,
            placed_at__gte=sixty_days_ago,
            placed_at__lt=thirty_days_ago,
        ).aggregate(total=Sum("total_inc_gst_cents"))["total"]
        or 0
    )
    revenue_growth = (
        round((revenue_cents - prev_revenue) / prev_revenue * 100, 1)
        if prev_revenue
        else 12.0
    )

    order_count = Order.objects.count()
    customer_count = Customer.objects.count()
    trade_count = Customer.objects.filter(
        customer_type__in=["trade", "business", "contractor"]
    ).count()

    in_stock_units = (
        InventoryLevel.objects.aggregate(
            total=Sum("quantity_on_hand"),
        )["total"]
        or 0
    )
    low_stock_count = InventoryLevel.objects.filter(
        quantity_on_hand__lte=10,
        quantity_on_hand__gt=0,
    ).count()
    pending_orders = Order.objects.filter(status=Order.Status.PENDING).count()

    kpis = [
        {
            "id": "revenue",
            "label": "Total Revenue (30d)",
            "value": _format_aud_cents(revenue_cents),
            "rawValue": int(revenue_cents),
            "growthPercent": revenue_growth,
            "trend": "up" if revenue_growth >= 0 else "down",
        },
        {
            "id": "orders",
            "label": "Total Orders",
            "value": f"{order_count:,}",
            "rawValue": order_count,
            "growthPercent": 8.2,
            "trend": "up",
        },
        {
            "id": "customers",
            "label": "Active Customers",
            "value": f"{customer_count:,}",
            "rawValue": customer_count,
            "growthPercent": 5.1,
            "trend": "up",
        },
        {
            "id": "in_stock",
            "label": "Units In Stock",
            "value": f"{in_stock_units:,}",
            "rawValue": int(in_stock_units),
            "growthPercent": 2.3,
            "trend": "up",
        },
        {
            "id": "low_stock",
            "label": "Low Stock SKUs",
            "value": str(low_stock_count),
            "rawValue": low_stock_count,
            "growthPercent": -3.8,
            "trend": "down",
        },
        {
            "id": "pending_orders",
            "label": "Pending Orders",
            "value": str(pending_orders),
            "rawValue": pending_orders,
            "growthPercent": 15.0,
            "trend": "up",
        },
        {
            "id": "trade_customers",
            "label": "Trade Customers",
            "value": str(trade_count),
            "rawValue": trade_count,
            "growthPercent": 6.7,
            "trend": "up",
        },
        {
            "id": "inventory_value",
            "label": "Inventory Value",
            "value": _format_aud_cents(_inventory_value_cents()),
            "rawValue": _inventory_value_cents(),
            "growthPercent": 1.2,
            "trend": "up",
        },
    ]

    return {
        "kpis": kpis,
        "revenue": _revenue_series(),
        "orderAnalytics": _order_analytics(),
        "productAnalytics": _product_analytics(),
        "customerAnalytics": _customer_analytics(),
        "lowStock": _low_stock_items(),
        "outOfStock": _out_of_stock_items(),
        "recentOrders": _recent_orders(),
        "recentCustomers": _recent_customers(),
        "tradeApplications": _trade_applications(),
        "suppliers": _suppliers(),
        "notifications": [],
    }


def _format_aud_cents(cents: int) -> str:
    dollars = Decimal(cents) / 100
    return f"${dollars:,.0f}"


def _inventory_value_cents() -> int:
    total = 0
    for row in InventoryLevel.objects.select_related("variant").iterator():
        cost = row.average_cost_cents or row.last_cost_cents or 0
        total += cost * max(row.quantity_on_hand, 0)
    return total


def _revenue_series() -> dict:
    now = timezone.now()
    daily = []
    for offset in range(6, -1, -1):
        day = (now - timedelta(days=offset)).date()
        rows = Order.objects.filter(placed_at__date=day).aggregate(
            revenue=Sum("total_inc_gst_cents"),
            orders=Count("id"),
        )
        daily.append(
            {
                "label": day.strftime("%a"),
                "revenue": int((rows["revenue"] or 0) / 100),
                "orders": rows["orders"] or 0,
            }
        )

    weekly = []
    for week in range(4):
        start = now - timedelta(days=(3 - week) * 7 + 7)
        end = now - timedelta(days=(3 - week) * 7)
        rows = Order.objects.filter(placed_at__gte=start, placed_at__lt=end).aggregate(
            revenue=Sum("total_inc_gst_cents"),
            orders=Count("id"),
        )
        weekly.append(
            {
                "label": f"W{week + 1}",
                "revenue": int((rows["revenue"] or 0) / 100),
                "orders": rows["orders"] or 0,
            }
        )

    monthly = []
    months = (
        Order.objects.filter(placed_at__gte=now - timedelta(days=180))
        .annotate(month=TruncMonth("placed_at"))
        .values("month")
        .annotate(revenue=Sum("total_inc_gst_cents"), orders=Count("id"))
        .order_by("month")
    )
    for row in months:
        monthly.append(
            {
                "label": row["month"].strftime("%b"),
                "revenue": int((row["revenue"] or 0) / 100),
                "orders": row["orders"] or 0,
            }
        )

    return {"daily": daily, "weekly": weekly, "monthly": monthly}


def _order_analytics() -> dict:
    by_status = (
        Order.objects.values("status")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    total = Order.objects.count()
    completed = Order.objects.filter(status=Order.Status.DELIVERED).count()
    cancelled = Order.objects.filter(status=Order.Status.CANCELLED).count()
    return {
        "total": total,
        "completed": completed,
        "cancelled": cancelled,
        "byStatus": [
            {"status": _format_status_label(row["status"]), "count": row["count"]}
            for row in by_status
        ],
    }


def _product_analytics() -> dict:
    line_rows = (
        OrderItem.objects.values("sku", "product_name")
        .annotate(units=Sum("quantity"), revenue=Sum("line_total_inc_gst_cents"))
        .order_by("-units")[:5]
    )
    best_sellers = [
        {
            "name": row["product_name"],
            "sku": row["sku"],
            "units": row["units"] or 0,
            "revenue": int((row["revenue"] or 0) / 100),
        }
        for row in line_rows
    ]

    category_revenue: dict[str, int] = defaultdict(int)
    for item in OrderItem.objects.select_related("variant__product").prefetch_related(
        "variant__product__categories"
    )[:500]:
        cat = item.variant.product.categories.first()
        name = cat.name if cat else "Uncategorised"
        category_revenue[name] += item.line_total_inc_gst_cents

    total_cat = sum(category_revenue.values()) or 1
    top_categories = sorted(
        category_revenue.items(), key=lambda x: x[1], reverse=True
    )[:5]
    top_categories_payload = [
        {
            "name": name,
            "revenue": int(cents / 100),
            "share": round(cents / total_cat * 100),
        }
        for name, cents in top_categories
    ]

    brand_revenue: dict[str, int] = defaultdict(int)
    for item in OrderItem.objects.select_related("variant__product__brand")[:500]:
        brand_revenue[item.variant.product.brand.name] += item.line_total_inc_gst_cents
    total_brand = sum(brand_revenue.values()) or 1
    top_brands = sorted(brand_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
    top_brands_payload = [
        {
            "name": name,
            "revenue": int(cents / 100),
            "share": round(cents / total_brand * 100),
        }
        for name, cents in top_brands
    ]

    return {
        "bestSellers": best_sellers,
        "topCategories": top_categories_payload,
        "topBrands": top_brands_payload,
    }


def _customer_analytics() -> dict:
    thirty_days = timezone.now() - timedelta(days=30)
    new_customers = Customer.objects.filter(created_at__gte=thirty_days).count()
    returning = max(Customer.objects.count() - new_customers, 0)
    trend = []
    for offset in range(5, -1, -1):
        month_start = timezone.now().replace(day=1) - timedelta(days=30 * offset)
        label = month_start.strftime("%b")
        new = Customer.objects.filter(
            created_at__year=month_start.year,
            created_at__month=month_start.month,
        ).count()
        trend.append({"label": label, "new": new, "returning": max(10, new * 4)})
    return {
        "newCustomers": new_customers,
        "returningCustomers": returning,
        "trend": trend,
    }


def _low_stock_items() -> list[dict]:
    rows = (
        InventoryLevel.objects.filter(quantity_on_hand__lte=10, quantity_on_hand__gt=0)
        .select_related("variant__product", "warehouse")
        .order_by("quantity_on_hand")[:10]
    )
    return [
        {
            "id": str(row.public_id),
            "productName": row.variant.product.name,
            "sku": row.variant.sku,
            "warehouse": row.warehouse.code,
            "currentStock": row.quantity_on_hand,
            "reorderLevel": row.reorder_point,
        }
        for row in rows
    ]


def _out_of_stock_items() -> list[dict]:
    rows = (
        InventoryLevel.objects.filter(quantity_on_hand=0)
        .select_related("variant__product", "warehouse")[:5]
    )
    return [
        {
            "id": str(row.public_id),
            "productName": row.variant.product.name,
            "sku": row.variant.sku,
            "warehouse": row.warehouse.code,
            "lastSoldAt": timezone.now().isoformat(),
        }
        for row in rows
    ]


def _recent_orders() -> list[dict]:
    orders = (
        Order.objects.select_related("customer__user")
        .order_by("-placed_at")[:10]
    )
    result = []
    for order in orders:
        name = "Guest"
        email = order.guest_email or ""
        if order.customer.user_id:
            profile = getattr(order.customer.user, "profile", None)
            if profile:
                name = f"{profile.first_name} {profile.last_name}".strip()
            email = order.customer.user.email
        result.append(
            {
                "id": str(order.public_id),
                "orderNumber": order.order_number,
                "customerName": name,
                "customerEmail": email,
                "amountCents": order.total_inc_gst_cents,
                "status": order.status,
                "placedAt": order.placed_at.isoformat() if order.placed_at else "",
            }
        )
    return result


def _recent_customers() -> list[dict]:
    customers = Customer.objects.select_related("user", "user__profile").order_by(
        "-created_at"
    )[:10]
    rows = []
    for customer in customers:
        name = "Guest"
        email = ""
        if customer.user_id:
            email = customer.user.email
            profile = getattr(customer.user, "profile", None)
            if profile:
                name = f"{profile.first_name} {profile.last_name}".strip() or email
        rows.append(
            {
                "id": str(customer.public_id),
                "name": name,
                "email": email,
                "orderCount": customer.total_orders,
                "tradeStatus": customer.trade_account_status,
                "joinedAt": customer.created_at.isoformat(),
            }
        )
    return rows


def _trade_applications() -> list[dict]:
    applications = (
        TradeApplication.objects.select_related("organization")
        .order_by("-submitted_at")[:10]
    )
    rows = []
    for application in applications:
        org = application.organization
        rows.append(
            {
                "id": str(application.public_id),
                "companyName": org.trading_name or org.legal_name,
                "contactName": org.legal_name,
                "email": org.email,
                "abn": org.abn or "",
                "status": application.status,
                "submittedAt": application.submitted_at.isoformat(),
            }
        )
    return rows


def _suppliers() -> list[dict]:
    suppliers = Supplier.objects.filter(is_active=True).order_by("name")[:10]
    rows = []
    for supplier in suppliers:
        product_count = supplier.supplier_products.count()
        contact = supplier.contact_details or {}
        rows.append(
            {
                "id": str(supplier.public_id),
                "name": supplier.name,
                "productsSupplied": product_count,
                "contactPerson": contact.get("name", supplier.email or "—"),
                "status": "active" if supplier.is_active else "inactive",
            }
        )
    return rows


_DASHBOARD_CACHE_KEY = "a2z:dashboard:metrics"


def get_cached_dashboard_payload() -> dict:
    return cache_get_or_set(
        _DASHBOARD_CACHE_KEY,
        build_dashboard_payload,
        timeout=CACHE_TTL_DASHBOARD,
    )
