"""Admin customer 360° detail payload."""
from __future__ import annotations

from uuid import UUID

from django.db.models import Count, Sum

from apps.core.exceptions import NotFoundError
from apps.customers.models import Customer
from apps.crm.services import CrmTimelineService
from apps.erp.services.party import PartyService
from apps.orders.models import Order
from apps.orders.serializers import OrderSummarySerializer
from apps.quotes.serializers import serialize_quote
from apps.quotes.services import QuoteService
from apps.trade_accounts.models import TradeAccount


def _customer_name(customer: Customer) -> str:
    if customer.user_id:
        profile = getattr(customer.user, "profile", None)
        if profile and (profile.first_name or profile.last_name):
            return f"{profile.first_name} {profile.last_name}".strip()
        return customer.user.email
    org = customer.organization
    if org:
        return org.trading_name or org.legal_name
    return "Guest"


def _customer_email(customer: Customer) -> str:
    if customer.user_id:
        return customer.user.email or ""
    org = customer.organization
    return org.email if org else ""


def _customer_phone(customer: Customer) -> str:
    if customer.user_id:
        profile = getattr(customer.user, "profile", None)
        if profile and profile.phone:
            return profile.phone
    org = customer.organization
    return org.phone if org else ""


def _serialize_organization(customer: Customer) -> dict | None:
    org = customer.organization
    if not org:
        return None
    return {
        "id": str(org.public_id),
        "legalName": org.legal_name,
        "tradingName": org.trading_name or org.legal_name,
        "abn": org.abn or "",
        "email": org.email,
        "phone": org.phone,
        "segment": org.customer_segment,
    }


def _serialize_trade_account(customer: Customer) -> dict | None:
    account: TradeAccount | None = None
    if customer.organization_id:
        account = getattr(customer.organization, "trade_account", None)
        if account is None:
            account = TradeAccount.objects.filter(organization=customer.organization).first()

    if not account and not customer.trade_account_status:
        return None

    if account:
        return {
            "id": str(account.public_id),
            "accountNumber": account.account_number,
            "status": account.status,
            "tier": account.tier,
            "creditLimitCents": account.credit_limit_cents,
            "creditUsedCents": account.credit_used_cents,
            "creditAvailableCents": account.credit_available_cents,
            "paymentTermsDays": account.payment_terms_days,
        }

    return {
        "id": None,
        "accountNumber": None,
        "status": customer.trade_account_status,
        "tier": None,
        "creditLimitCents": customer.credit_limit_cents,
        "creditUsedCents": 0,
        "creditAvailableCents": customer.credit_limit_cents,
        "paymentTermsDays": customer.payment_terms_days,
    }


def build_admin_customer_detail(customer_id: UUID) -> dict:
    customer = (
        Customer.objects.select_related(
            "user",
            "user__profile",
            "organization",
            "organization__trade_account",
        )
        .filter(public_id=customer_id)
        .first()
    )
    if not customer:
        raise NotFoundError("Customer not found.")

    party = PartyService.ensure_for_customer(customer)

    orders = (
        Order.objects.filter(customer=customer)
        .annotate(item_count=Count("items"))
        .order_by("-placed_at")[:50]
    )
    quotes_qs = QuoteService.list_quotes(customer_id=customer.public_id).order_by("-created_at")
    quote_count = quotes_qs.count()
    accepted_quotes = quotes_qs.filter(
        status__in=["accepted", "converted", "sent", "approved"]
    ).aggregate(total=Sum("total_inc_gst_cents"))
    accepted_quote_cents = int(accepted_quotes["total"] or 0)
    quotes = list(quotes_qs[:50])

    paid_total = (
        Order.objects.filter(
            customer=customer,
            status__in=[
                Order.Status.PAID,
                Order.Status.PACKED,
                Order.Status.SHIPPED,
                Order.Status.DELIVERED,
            ],
        ).aggregate(total=Sum("total_inc_gst_cents"))
    )
    total_spent_cents = int(paid_total["total"] or customer.total_spent_cents or 0)
    order_count = customer.total_orders or orders.count()

    crm_activities = CrmTimelineService.get_feed(
        party_id=party.public_id,
        customer_id=customer.public_id,
        limit=50,
    )

    return {
        "profile": {
            "id": str(customer.public_id),
            "name": _customer_name(customer),
            "email": _customer_email(customer),
            "phone": _customer_phone(customer),
            "customerType": customer.customer_type,
            "tradeStatus": customer.trade_account_status,
            "joinedAt": customer.created_at.isoformat(),
            "organization": _serialize_organization(customer),
        },
        "partyId": str(party.public_id),
        "lifetimeValue": {
            "totalSpentCents": total_spent_cents,
            "orderCount": order_count,
            "averageOrderCents": total_spent_cents // max(order_count, 1),
            "quoteCount": quote_count,
            "acceptedQuoteValueCents": accepted_quote_cents,
        },
        "tradeAccount": _serialize_trade_account(customer),
        "orders": OrderSummarySerializer(orders, many=True).data,
        "quotes": [serialize_quote(quote) for quote in quotes],
        "crmActivities": crm_activities,
    }
