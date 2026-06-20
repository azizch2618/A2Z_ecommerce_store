"""Quote & sales workflow API tests."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.rbac import PermissionCodename
from apps.accounts.services import PermissionService, RoleService
from apps.catalog.models import Brand, Product, ProductVariant
from apps.customers.models import Customer
from apps.pricing.models import PriceList, PriceListItem
from apps.trade_accounts.models import Quote

User = get_user_model()


class QuoteApiTests(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        call_command("seed_erp_foundation", verbosity=0)

        self.manager = User.objects.create_user(
            email="quotes-manager@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.manager, RoleSlug.MANAGER)

        self.sales_rep = User.objects.create_user(
            email="quotes-sales@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.sales_rep, RoleSlug.SALES_REP)

        self.warehouse = User.objects.create_user(
            email="quotes-wh@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.warehouse, RoleSlug.WAREHOUSE_MANAGER)

        self.customer_user = User.objects.create_user(
            email="quotes-customer@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            customer_type="trade",
        )
        RoleService.assign_role(self.customer_user, RoleSlug.TRADE_CUSTOMER)

        brand = Brand.objects.create(name="Bosch", slug="bosch-quotes")
        product = Product.objects.create(
            brand=brand,
            name="Angle Grinder",
            slug="angle-grinder-quotes",
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="GRD-QUOTE-001",
            is_default=True,
            is_active=True,
        )
        price_list = PriceList.objects.create(
            name="Retail Quotes",
            slug="retail-quotes",
            is_active=True,
        )
        PriceListItem.objects.create(
            price_list=price_list,
            variant=self.variant,
            unit_price_ex_gst_cents=10000,
        )

    def _create_quote_with_line(self, *, customer_id: str | None = None, unit_price: int = 10000):
        self.client.force_authenticate(user=self.sales_rep)
        create_resp = self.client.post(
            "/api/v1/quotes/admin/",
            {"customerId": customer_id or str(self.customer.public_id), "notes": "Test quote"},
            format="json",
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        quote_id = create_resp.data["id"]
        line_resp = self.client.post(
            f"/api/v1/quotes/admin/{quote_id}/lines/",
            {
                "variantId": str(self.variant.public_id),
                "quantity": 2,
                "unitPriceExGstCents": unit_price,
            },
            format="json",
        )
        self.assertEqual(line_resp.status_code, status.HTTP_201_CREATED)
        return quote_id

    def test_sales_rep_can_view_quote_dashboard(self):
        self.client.force_authenticate(user=self.sales_rep)
        response = self.client.get("/api/v1/quotes/admin/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("draftQuotes", response.data)

    def test_warehouse_manager_cannot_access_quotes(self):
        self.client.force_authenticate(user=self.warehouse)
        response = self.client.get("/api/v1/quotes/admin/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rbac_permissions_include_quotes(self):
        self.assertTrue(
            PermissionService.has_permission(self.manager, PermissionCodename.QUOTES_APPROVE)
        )
        self.assertTrue(
            PermissionService.has_permission(self.sales_rep, PermissionCodename.QUOTES_MANAGE)
        )
        self.assertFalse(
            PermissionService.has_permission(self.sales_rep, PermissionCodename.QUOTES_APPROVE)
        )

    def test_below_threshold_auto_approves_on_submit(self):
        quote_id = self._create_quote_with_line(unit_price=10000)
        submit_resp = self.client.post(f"/api/v1/quotes/admin/{quote_id}/submit/", format="json")
        self.assertEqual(submit_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(submit_resp.data["status"], Quote.Status.APPROVED)

    def test_above_threshold_requires_manager_approval(self):
        from apps.quotes.services import QuoteService

        quote = QuoteService.create_quote(
            actor=self.sales_rep,
            data={"customer_id": self.customer.public_id},
        )
        QuoteService.add_line(
            quote=quote,
            actor=self.sales_rep,
            data={
                "variant_id": self.variant.public_id,
                "quantity": 2,
                "unit_price_ex_gst_cents": 300_000,
            },
        )
        quote.refresh_from_db()
        self.assertGreaterEqual(quote.total_inc_gst_cents, 500_000)

        quote = QuoteService.submit_for_approval(quote=quote, actor=self.sales_rep)
        self.assertEqual(quote.status, Quote.Status.PENDING_APPROVAL)

        self.client.force_authenticate(user=self.sales_rep)
        approve_resp = self.client.post(
            f"/api/v1/quotes/admin/{quote.public_id}/approve/",
            format="json",
        )
        self.assertEqual(approve_resp.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.manager)
        approve_resp = self.client.post(
            f"/api/v1/quotes/admin/{quote.public_id}/approve/",
            {"comment": "Looks good"},
            format="json",
        )
        self.assertEqual(approve_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(approve_resp.data["status"], Quote.Status.APPROVED)

    def test_full_quote_lifecycle_to_order(self):
        quote_id = self._create_quote_with_line()
        self.client.post(f"/api/v1/quotes/admin/{quote_id}/submit/", format="json")
        send_resp = self.client.post(f"/api/v1/quotes/admin/{quote_id}/send/", format="json")
        self.assertEqual(send_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(send_resp.data["status"], Quote.Status.SENT)

        self.client.force_authenticate(user=self.customer_user)
        accept_resp = self.client.post(f"/api/v1/quotes/my/{quote_id}/accept/", format="json")
        self.assertEqual(accept_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(accept_resp.data["status"], Quote.Status.ACCEPTED)

        self.client.force_authenticate(user=self.sales_rep)
        convert_resp = self.client.post(f"/api/v1/quotes/admin/{quote_id}/convert/", format="json")
        self.assertEqual(convert_resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("orderNumber", convert_resp.data)
        self.assertEqual(convert_resp.data["quote"]["status"], Quote.Status.CONVERTED)

    def test_quote_pdf_endpoint(self):
        quote_id = self._create_quote_with_line()
        self.client.force_authenticate(user=self.sales_rep)
        pdf_resp = self.client.get(f"/api/v1/quotes/admin/{quote_id}/pdf/")
        self.assertEqual(pdf_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(pdf_resp["Content-Type"], "application/pdf")
        self.assertTrue(pdf_resp.content.startswith(b"%PDF"))

    def test_customer_can_list_sent_quotes(self):
        quote_id = self._create_quote_with_line()
        self.client.post(f"/api/v1/quotes/admin/{quote_id}/submit/", format="json")
        self.client.post(f"/api/v1/quotes/admin/{quote_id}/send/", format="json")

        self.client.force_authenticate(user=self.customer_user)
        list_resp = self.client.get("/api/v1/quotes/my/")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        ids = [row["id"] for row in list_resp.data["data"]]
        self.assertIn(quote_id, ids)
