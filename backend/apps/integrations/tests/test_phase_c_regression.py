"""Phase C regression suite for route/API/RBAC integrity."""

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Category, Product, ProductVariant
from apps.customers.models import Customer, Organization
from apps.inventory.models import InventoryLevel, Warehouse
from apps.pricing.models import PriceList, PriceListItem
from apps.trade_accounts.models import TradeApplication

User = get_user_model()


class PhaseCRegressionSuite(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()

        self.manager = User.objects.create_user(
            email="regression-manager@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.manager, RoleSlug.MANAGER)

        self.warehouse_user = User.objects.create_user(
            email="regression-wh@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.warehouse_user, RoleSlug.WAREHOUSE_MANAGER)

        self.customer_user = User.objects.create_user(
            email="regression-customer@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        RoleService.assign_role(self.customer_user, RoleSlug.CUSTOMER)
        Customer.objects.create(user=self.customer_user, customer_type="retail")

        brand = Brand.objects.create(name="Bosch", slug="bosch-reg", is_active=True)
        category = Category.objects.create(name="Tools", slug="tools-reg", is_active=True)
        product = Product.objects.create(
            brand=brand,
            name="Impact Driver",
            slug="impact-driver-reg",
            is_active=True,
        )
        product.categories.add(category)
        variant = ProductVariant.objects.create(
            product=product,
            sku="REG-001",
            is_default=True,
            is_active=True,
        )
        price_list = PriceList.objects.create(name="Retail", slug="retail-reg", is_active=True)
        PriceListItem.objects.create(
            price_list=price_list,
            variant=variant,
            unit_price_ex_gst_cents=10900,
        )
        wh = Warehouse.objects.create(code="REG1", name="Regression DC", is_active=True)
        InventoryLevel.objects.create(
            warehouse=wh,
            variant=variant,
            quantity_on_hand=50,
            quantity_reserved=0,
        )

    def test_no_broken_core_routes(self):
        response_specs = [
            (self.client.get("/api/v1/health/"), [status.HTTP_200_OK]),
            (self.client.get("/api/v1/products/"), [status.HTTP_200_OK]),
            (self.client.get("/api/v1/categories/"), [status.HTTP_200_OK]),
            (self.client.get("/api/v1/brands/"), [status.HTTP_200_OK]),
            (self.client.get("/api/v1/payments/config/"), [status.HTTP_200_OK]),
            (self.client.get("/api/v1/orders/"), [status.HTTP_401_UNAUTHORIZED]),
            (self.client.get("/api/v1/cart/", HTTP_X_SESSION_KEY="regression-guest"), [status.HTTP_200_OK]),
        ]
        for response, allowed in response_specs:
            self.assertIn(response.status_code, allowed)

    def test_admin_api_endpoints_do_not_500_for_authorized_user(self):
        self.client.force_authenticate(self.manager)
        endpoints = [
            "/api/v1/admin/categories/",
            "/api/v1/admin/brands/",
            "/api/v1/suppliers/admin/",
            "/api/v1/inventory/admin/warehouses/",
            "/api/v1/suppliers/purchase-orders/",
            "/api/v1/trade-accounts/admin/applications/",
            "/api/v1/analytics/admin/reports/",
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_no_rbac_leak_customer_cannot_access_admin_modules(self):
        self.client.force_authenticate(self.customer_user)
        protected_endpoints = [
            "/api/v1/admin/categories/",
            "/api/v1/admin/brands/",
            "/api/v1/suppliers/admin/",
            "/api/v1/inventory/admin/warehouses/",
            "/api/v1/trade-accounts/admin/applications/",
            "/api/v1/analytics/admin/reports/",
        ]
        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_no_permission_bypass_warehouse_cannot_approve_trade(self):
        org = Organization.objects.create(
            legal_name="Regression Trade Co",
            email="reg-trade@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        application = TradeApplication.objects.create(organization=org, status="pending")
        self.client.force_authenticate(self.warehouse_user)
        response = self.client.post(
            f"/api/v1/trade-accounts/admin/applications/{application.public_id}/review/",
            {"status": "approved", "credit_limit_cents": 100000},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_permission_bypass_anonymous_cannot_mutate_admin_resources(self):
        post_attempts = [
            self.client.post("/api/v1/admin/categories/", {"name": "Blocked"}, format="json"),
            self.client.post("/api/v1/admin/brands/", {"name": "Blocked"}, format="json"),
            self.client.post("/api/v1/suppliers/admin/", {"code": "B", "name": "Blocked"}, format="json"),
            self.client.post(
                "/api/v1/inventory/admin/warehouses/",
                {"code": "B1", "name": "Blocked", "warehouse_type": "distribution"},
                format="json",
            ),
        ]
        for response in post_attempts:
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
