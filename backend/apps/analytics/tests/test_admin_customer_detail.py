"""Admin customer detail API tests."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.crm.constants import ActivityType
from apps.crm.models import CrmActivity
from apps.customers.models import Customer, Organization
from apps.erp.services.party import PartyService
from apps.orders.models import Order
from apps.trade_accounts.models import Quote, TradeAccount

User = get_user_model()


class AdminCustomerDetailAPITestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.admin = User.objects.create_user(
            email="customer-admin@example.com",
            password="TestPass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.admin, RoleSlug.ADMIN)

        self.org = Organization.objects.create(
            legal_name="Metro Electrical Pty Ltd",
            trading_name="Metro Electrical",
            abn="53004085616",
            email="accounts@metro.example.com",
            phone="0299998888",
            customer_segment=Organization.CustomerSegment.TRADE,
        )
        self.user = User.objects.create_user(
            email="buyer@metro.example.com",
            password="TestPass123!",
        )
        self.customer = Customer.objects.create(
            user=self.user,
            organization=self.org,
            customer_type=Customer.CustomerType.TRADE,
            trade_account_status=Customer.TradeStatus.APPROVED,
            credit_limit_cents=500_000,
            total_orders=2,
            total_spent_cents=150_000,
        )
        self.trade_account = TradeAccount.objects.create(
            organization=self.org,
            account_number="TA-1001",
            status=TradeAccount.Status.APPROVED,
            credit_limit_cents=500_000,
            credit_used_cents=50_000,
        )
        self.party = PartyService.ensure_for_customer(self.customer)

        Order.objects.create(
            customer=self.customer,
            order_number="A2Z-TEST-001",
            status=Order.Status.DELIVERED,
            payment_status=Order.PaymentStatus.PAID,
            subtotal_ex_gst_cents=90_000,
            gst_total_cents=9_000,
            total_inc_gst_cents=99_000,
            currency_code="AUD",
            placed_at=timezone.now(),
        )

        Quote.objects.create(
            customer=self.customer,
            party=self.party,
            trade_account=self.trade_account,
            quote_number="Q-1001",
            status=Quote.Status.SENT,
            valid_until=timezone.now() + timedelta(days=14),
            total_inc_gst_cents=45_000,
        )

        CrmActivity.objects.create(
            party=self.party,
            activity_type=ActivityType.CALL,
            subject="Follow-up on cable order",
            description="Discussed bulk pricing.",
            created_by=self.admin,
        )

    def test_customer_detail_requires_auth(self):
        response = self.client.get(
            f"/api/v1/analytics/admin/customers/{self.customer.public_id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_detail_payload(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(
            f"/api/v1/analytics/admin/customers/{self.customer.public_id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profile"]["email"], "buyer@metro.example.com")
        self.assertEqual(response.data["profile"]["organization"]["legalName"], "Metro Electrical Pty Ltd")
        self.assertEqual(response.data["lifetimeValue"]["totalSpentCents"], 99_000)
        self.assertEqual(response.data["lifetimeValue"]["orderCount"], 2)
        self.assertEqual(response.data["tradeAccount"]["accountNumber"], "TA-1001")
        self.assertEqual(len(response.data["orders"]), 1)
        self.assertEqual(len(response.data["quotes"]), 1)
        self.assertGreaterEqual(len(response.data["crmActivities"]), 1)

    def test_customer_detail_not_found(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(
            "/api/v1/analytics/admin/customers/00000000-0000-0000-0000-000000000099/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
