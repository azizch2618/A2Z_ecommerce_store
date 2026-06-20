"""Seed demo users, customers, orders, and analytics."""

from __future__ import annotations

import random
import uuid
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.constants import RoleSlug
from apps.accounts.models import UserProfile
from apps.accounts.services import RoleService
from apps.analytics.models import AnalyticsEvent
from apps.catalog.models import Brand, Product, ProductVariant
from apps.core.demo.catalog import DEMO_ACCOUNTS, DEMO_PASSWORD
from apps.customers.models import Address, Customer, Organization
from apps.inventory.models import InventoryLevel, InventoryTransaction, Warehouse
from apps.inventory.services import InventoryService
from apps.orders.models import Order, Payment, Shipment, Wishlist, WishlistItem
from apps.orders.services import OrderService
from apps.pricing.models import PriceList, PriceListItem
from apps.pricing.services import PricingService

User = get_user_model()

ADDRESS_SYDNEY = {
    "line1": "42 George Street",
    "line2": "Level 5",
    "suburb": "Sydney",
    "state": "NSW",
    "postcode": "2000",
    "country": "AU",
    "label": "Office",
}

ADDRESS_MELB = {
    "line1": "100 Collins Street",
    "line2": "",
    "suburb": "Melbourne",
    "state": "VIC",
    "postcode": "3000",
    "country": "AU",
    "label": "Warehouse",
}


def seed_users_and_customers() -> dict[str, User]:
    RoleService.ensure_system_roles()
    users: dict[str, User] = {}

    for account in DEMO_ACCOUNTS:
        user, created = User.objects.get_or_create(
            email=account["email"],
            defaults={
                "is_staff": account.get("is_staff", False),
                "is_active": True,
                "email_verified_at": timezone.now(),
            },
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=["password"])

        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                "first_name": account["first_name"],
                "last_name": account["last_name"],
                "phone": "0412 345 678",
            },
        )

        org = None
        if org_data := account.get("organization"):
            org, _ = Organization.objects.update_or_create(
                abn=org_data["abn"],
                defaults={
                    "legal_name": org_data["legal_name"],
                    "trading_name": org_data["trading_name"],
                    "email": account["email"],
                    "customer_segment": org_data["segment"],
                    "abn_verified": True,
                    "is_active": True,
                },
            )

        customer_type = account.get("customer_type", "retail")
        customer, _ = Customer.objects.update_or_create(
            user=user,
            defaults={
                "customer_type": customer_type,
                "organization": org,
                "trade_account_status": (
                    Customer.TradeStatus.APPROVED
                    if customer_type in {"trade", "business", "contractor"}
                    else None
                ),
                "credit_limit_cents": 50_000_000 if org else 0,
                "payment_terms_days": 30 if org else None,
            },
        )

        Address.objects.get_or_create(
            customer=customer,
            line1=ADDRESS_SYDNEY["line1"],
            suburb=ADDRESS_SYDNEY["suburb"],
            postcode=ADDRESS_SYDNEY["postcode"],
            defaults={
                **ADDRESS_SYDNEY,
                "is_default_billing": True,
                "is_default_shipping": True,
            },
        )

        role_slug = account.get("role", RoleSlug.CUSTOMER)
        if role_slug == RoleSlug.MANAGER:
            RoleService.assign_role(user, RoleSlug.MANAGER)
        elif role_slug == RoleSlug.TRADE_CUSTOMER:
            RoleService.assign_customer_role(
                user, customer_type, organization=org
            )
        else:
            RoleService.assign_customer_role(user, customer_type)

        users[account["email"]] = user

    return users


def _create_demo_order(
    *,
    customer: Customer,
    variant: ProductVariant,
    quantity: int,
    status: str,
    days_ago: int,
    warehouse: Warehouse,
) -> Order:
    placed_at = timezone.now() - timedelta(days=days_ago)
    unit_ex = PriceListItem.objects.filter(
        variant=variant, price_list__slug="retail"
    ).values_list("unit_price_ex_gst_cents", flat=True).first() or 10000
    unit_gst = PricingService.calculate_gst(unit_ex)
    shipping_ex = 1500
    shipping_gst = PricingService.calculate_gst(shipping_ex)
    line_ex = unit_ex * quantity
    line_gst = unit_gst * quantity

    order = Order.objects.create(
        order_number=f"A2Z-DEMO-{uuid.uuid4().hex[:8].upper()}",
        customer=customer,
        organization=customer.organization,
        status=status,
        payment_status=(
            Order.PaymentStatus.PAID
            if status != Order.Status.PENDING
            and status != Order.Status.CANCELLED
            else Order.PaymentStatus.PENDING
        ),
        currency_code="AUD",
        billing_address=ADDRESS_SYDNEY,
        shipping_address=ADDRESS_MELB,
        shipping_method={"id": str(uuid.uuid4()), "name": "Standard", "carrier": "Australia Post"},
        payment_method="card",
        placed_at=placed_at,
        paid_at=placed_at if status != Order.Status.PENDING else None,
        shipped_at=placed_at + timedelta(days=2) if status in {
            Order.Status.SHIPPED, Order.Status.DELIVERED
        } else None,
        delivered_at=placed_at + timedelta(days=5) if status == Order.Status.DELIVERED else None,
        cancelled_at=placed_at if status == Order.Status.CANCELLED else None,
        subtotal_ex_gst_cents=line_ex,
        gst_total_cents=line_gst + shipping_gst,
        shipping_ex_gst_cents=shipping_ex,
        shipping_gst_cents=shipping_gst,
        total_inc_gst_cents=line_ex + line_gst + shipping_ex + shipping_gst,
    )

    from apps.orders.models import OrderItem

    OrderItem.objects.create(
        order=order,
        variant=variant,
        sku=variant.sku,
        product_name=variant.product.name,
        variant_name=variant.name,
        quantity=quantity,
        unit_price_ex_gst_cents=unit_ex,
        unit_gst_cents=unit_gst,
        gst_rate=Decimal("0.1000"),
        line_total_ex_gst_cents=line_ex,
        line_gst_cents=line_gst,
        line_total_inc_gst_cents=line_ex + line_gst,
    )

    if status != Order.Status.CANCELLED and status != Order.Status.PENDING:
        Payment.objects.create(
            order=order,
            payment_method="card",
            status=Payment.Status.PAID,
            amount_cents=order.total_inc_gst_cents,
            gst_cents=order.gst_total_cents,
            currency_code="AUD",
            paid_at=placed_at,
            idempotency_key=f"demo-{order.public_id}",
        )
        try:
            InventoryService.stock_out(
                sku=variant.sku,
                warehouse_code=warehouse.code,
                quantity=quantity,
                transaction_type=InventoryTransaction.TransactionType.SALE,
                reference_type="order",
                reference_id=order.id,
                sale_price_cents=unit_ex,
                notes=f"Demo order {order.order_number}",
            )
        except Exception:
            pass

    if status in {Order.Status.SHIPPED, Order.Status.DELIVERED}:
        Shipment.objects.create(
            order=order,
            carrier="Australia Post",
            tracking_number=f"AP{random.randint(100000, 999999)}",
            status=Shipment.Status.DELIVERED if status == Order.Status.DELIVERED else Shipment.Status.SHIPPED,
            shipped_at=order.shipped_at,
            delivered_at=order.delivered_at,
        )

    Customer.objects.filter(pk=customer.pk).update(
        total_orders=customer.total_orders + 1,
        total_spent_cents=customer.total_spent_cents + order.total_inc_gst_cents,
    )
    return order


@transaction.atomic
def seed_orders_and_wishlists(users: dict[str, User], variants: list[ProductVariant]) -> int:
    retail = Customer.objects.get(user=users["customer@demo.a2ztools.com"])
    trade = Customer.objects.get(user=users["trade@demo.a2ztools.com"])
    warehouse = Warehouse.objects.get(code="SYD1")

    scenarios = [
        (Order.Status.PENDING, retail, 2),
        (Order.Status.PAID, retail, 3),
        (Order.Status.PACKED, trade, 2),
        (Order.Status.SHIPPED, trade, 3),
        (Order.Status.DELIVERED, retail, 8),
        (Order.Status.CANCELLED, retail, 2),
    ]

    count = 0
    day = 75
    for index, variant in enumerate(variants):
        for status, customer, qty in scenarios:
            if index > 0 and status in {Order.Status.PENDING, Order.Status.CANCELLED}:
                continue
            for _ in range(1 if index > 2 else qty):
                _create_demo_order(
                    customer=customer,
                    variant=variant,
                    quantity=random.randint(1, 2),
                    status=status,
                    days_ago=day,
                    warehouse=warehouse,
                )
                count += 1
                day = max(1, day - 2)

    wishlist, _ = Wishlist.objects.get_or_create(customer=retail, is_default=True)
    for variant in variants[:4]:
        WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            variant=variant,
            defaults={"desired_quantity": 1},
        )

    trade_wishlist, _ = Wishlist.objects.get_or_create(customer=trade, is_default=True)
    WishlistItem.objects.get_or_create(
        wishlist=trade_wishlist,
        variant=variants[0],
        defaults={"desired_quantity": 2},
    )

    return count


def seed_analytics_events() -> int:
    now = timezone.now()
    events = []
    for days_ago in range(30, 0, -1):
        occurred = now - timedelta(days=days_ago)
        for _ in range(random.randint(40, 80)):
            events.append(
                AnalyticsEvent(
                    event_type="page_view",
                    session_id=f"demo-{uuid.uuid4().hex[:12]}",
                    properties={"path": "/products"},
                    occurred_at=occurred,
                )
            )
        for _ in range(random.randint(3, 12)):
            events.append(
                AnalyticsEvent(
                    event_type="purchase",
                    session_id=f"demo-{uuid.uuid4().hex[:12]}",
                    properties={"revenue_cents": random.randint(5000, 500000)},
                    occurred_at=occurred,
                )
            )
    AnalyticsEvent.objects.bulk_create(events, batch_size=500)
    return len(events)
