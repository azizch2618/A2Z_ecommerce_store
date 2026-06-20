"""Production security hardening tests."""
import uuid

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Product, ProductVariant
from apps.customers.models import Customer, Organization
from apps.inventory.models import InventoryLevel, Warehouse
from apps.orders.models import Cart, CartItem
from apps.pricing.models import PriceList, PriceListItem
from apps.trade_accounts.models import TradeAccount, TradeCreditAuditLog

User = get_user_model()

ADDRESS = {
    "line1": "1 George St",
    "suburb": "Sydney",
    "state": "NSW",
    "postcode": "2000",
    "country": "AU",
}


class SecretKeyConfigTestCase(APITestCase):
    def test_test_settings_use_non_default_secret(self):
        from django.conf import settings

        self.assertTrue(settings.SECRET_KEY)
        self.assertNotEqual(settings.SECRET_KEY, "django-insecure-change-me")


class ApiDocsProtectionTestCase(APITestCase):
    def test_schema_requires_staff_when_not_debug(self):
        with override_settings(DEBUG=False):
            response = self.client.get(reverse("schema"))
            self.assertIn(
                response.status_code,
                (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
            )

        staff = User.objects.create_user(
            email="staff@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        self.client.force_authenticate(staff)
        with override_settings(DEBUG=False):
            response = self.client.get(reverse("schema"))
            self.assertEqual(response.status_code, status.HTTP_200_OK)


class CartOwnershipTestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.user = User.objects.create_user(
            email="owner@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        self.customer = Customer.objects.create(user=self.user, customer_type="retail")
        RoleService.assign_role(self.user, RoleSlug.CUSTOMER)

        brand = Brand.objects.create(name="Makita", slug="makita")
        product = Product.objects.create(brand=brand, name="Drill", slug="drill", is_active=True)
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="DRL-001",
            is_default=True,
            is_active=True,
        )
        price_list = PriceList.objects.create(name="Retail", slug="retail", is_active=True)
        PriceListItem.objects.create(
            price_list=price_list,
            variant=self.variant,
            unit_price_ex_gst_cents=10000,
        )

        self.warehouse = Warehouse.objects.create(code="SYD1", name="Sydney", is_active=True)
        InventoryLevel.objects.create(
            warehouse=self.warehouse,
            variant=self.variant,
            quantity_on_hand=100,
            quantity_reserved=0,
        )

        self.guest_cart = Cart.objects.create(session_key="guest-session-abc", currency_code="AUD")
        CartItem.objects.create(
            cart=self.guest_cart,
            variant=self.variant,
            quantity=1,
            unit_price_cents=10000,
        )

        self.client.force_authenticate(self.user)

    def test_cannot_checkout_foreign_guest_cart(self):
        response = self.client.post(
            reverse("orders:order-list-create"),
            {
                "cart_id": str(self.guest_cart.public_id),
                "billing_address": ADDRESS,
                "shipping_method_id": str(uuid.uuid4()),
                "payment_method": "card",
            },
            format="json",
            HTTP_X_SESSION_KEY="wrong-session",
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    @override_settings(DEMO_AUTO_COMPLETE_PAYMENTS=True, STRIPE_SECRET_KEY="")
    def test_can_checkout_own_guest_cart_with_matching_session(self):
        response = self.client.post(
            reverse("orders:order-list-create"),
            {
                "cart_id": str(self.guest_cart.public_id),
                "billing_address": ADDRESS,
                "shipping_method_id": str(uuid.uuid4()),
                "payment_method": "card",
            },
            format="json",
            HTTP_X_SESSION_KEY="guest-session-abc",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


@override_settings(DEMO_AUTO_COMPLETE_PAYMENTS=True, STRIPE_SECRET_KEY="")
class TradeCreditSecurityTestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.user = User.objects.create_user(
            email="trade@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        self.organization = Organization.objects.create(
            legal_name="Trade Co Pty Ltd",
            trading_name="Trade Co",
            abn="51824753556",
            email="trade@example.com",
            customer_segment=Organization.CustomerSegment.TRADE,
        )
        self.customer = Customer.objects.create(
            user=self.user,
            organization=self.organization,
            customer_type="trade",
        )
        RoleService.assign_role(self.user, RoleSlug.CUSTOMER)

        self.trade_account = TradeAccount.objects.create(
            organization=self.organization,
            account_number="TA-001",
            status=TradeAccount.Status.APPROVED,
            credit_limit_cents=50_000_00,
            credit_used_cents=0,
        )

        brand = Brand.objects.create(name="Makita", slug="makita-trade")
        product = Product.objects.create(brand=brand, name="Saw", slug="saw", is_active=True)
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="SAW-001",
            is_default=True,
            is_active=True,
        )
        price_list = PriceList.objects.create(name="Retail", slug="retail-trade", is_active=True)
        PriceListItem.objects.create(
            price_list=price_list,
            variant=self.variant,
            unit_price_ex_gst_cents=10000,
        )

        self.warehouse = Warehouse.objects.create(code="SYD1", name="Sydney", is_active=True)
        InventoryLevel.objects.create(
            warehouse=self.warehouse,
            variant=self.variant,
            quantity_on_hand=100,
            quantity_reserved=0,
        )

        self.cart = Cart.objects.create(customer=self.customer, currency_code="AUD")
        CartItem.objects.create(
            cart=self.cart,
            variant=self.variant,
            quantity=1,
            unit_price_cents=10000,
        )

        self.client.force_authenticate(self.user)

    def test_trade_credit_requires_sufficient_limit(self):
        self.trade_account.credit_limit_cents = 100
        self.trade_account.save(update_fields=["credit_limit_cents", "updated_at"])

        response = self.client.post(
            reverse("orders:order-list-create"),
            {
                "cart_id": str(self.cart.public_id),
                "billing_address": ADDRESS,
                "shipping_method_id": str(uuid.uuid4()),
                "payment_method": "trade_credit",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_trade_credit_charges_account_and_audits(self):
        response = self.client.post(
            reverse("orders:order-list-create"),
            {
                "cart_id": str(self.cart.public_id),
                "billing_address": ADDRESS,
                "shipping_method_id": str(uuid.uuid4()),
                "payment_method": "trade_credit",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["payment_status"], "paid")

        self.trade_account.refresh_from_db()
        self.assertGreater(self.trade_account.credit_used_cents, 0)
        self.assertEqual(TradeCreditAuditLog.objects.count(), 1)

    def test_trade_credit_rejected_without_approved_account(self):
        self.trade_account.status = TradeAccount.Status.PENDING
        self.trade_account.save(update_fields=["status", "updated_at"])

        response = self.client.post(
            reverse("orders:order-list-create"),
            {
                "cart_id": str(self.cart.public_id),
                "billing_address": ADDRESS,
                "shipping_method_id": str(uuid.uuid4()),
                "payment_method": "trade_credit",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class CookieAuthTestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.user = User.objects.create_user(
            email="cookie@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        Customer.objects.create(user=self.user, customer_type="retail")
        RoleService.assign_role(self.user, RoleSlug.CUSTOMER)

    @override_settings(JWT_AUTH_COOKIE_ONLY=True)
    def test_login_sets_httponly_cookies(self):
        response = self.client.post(
            reverse("auth:login"),
            {"email": "cookie@example.com", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("a2z_access", response.cookies)
        self.assertIn("a2z_refresh", response.cookies)
        self.assertNotIn("tokens", response.data)
