"""Phase C production validation integration suite."""

import uuid
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Category, Product, ProductVariant
from apps.customers.models import Customer, Organization
from apps.inventory.models import InventoryLevel, Warehouse
from apps.orders.models import Cart, CartItem
from apps.pricing.models import PriceList, PriceListItem
from apps.suppliers.models import Supplier
from apps.trade_accounts.models import TradeApplication

User = get_user_model()

ADDRESS = {
    "line1": "1 George St",
    "suburb": "Sydney",
    "state": "NSW",
    "postcode": "2000",
    "country": "AU",
}


@override_settings(
    DEMO_AUTO_COMPLETE_PAYMENTS=False,
    STRIPE_SECRET_KEY="sk_test_fake",
    STRIPE_PUBLISHABLE_KEY="pk_test_fake",
    STRIPE_WEBHOOK_SECRET="whsec_test_fake",
)
class PhaseCIntegrationSuite(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        from django.core.management import call_command

        call_command("seed_erp_foundation", verbosity=0)

        self.manager = User.objects.create_user(
            email="phasec-manager@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.manager, RoleSlug.MANAGER)

        self.trade_reviewer = User.objects.create_user(
            email="phasec-trade-reviewer@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.trade_reviewer, RoleSlug.TRADE_REVIEWER)

        self.warehouse_user = User.objects.create_user(
            email="phasec-wh@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.warehouse_user, RoleSlug.WAREHOUSE_MANAGER)

        self.customer_user = User.objects.create_user(
            email="phasec-customer@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        RoleService.assign_role(self.customer_user, RoleSlug.CUSTOMER)
        self.customer = Customer.objects.create(user=self.customer_user, customer_type="retail")

        self.brand = Brand.objects.create(name="Makita", slug="makita-phase-c", is_active=True)
        self.category = Category.objects.create(
            name="Power Tools",
            slug="power-tools-phase-c",
            is_active=True,
        )
        self.product = Product.objects.create(
            brand=self.brand,
            name="Cordless Drill",
            slug="cordless-drill-phase-c",
            is_active=True,
        )
        self.product.categories.add(self.category)
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="DRILL-PHASEC-001",
            is_default=True,
            is_active=True,
        )

        self.price_list = PriceList.objects.create(name="Retail", slug="retail-phase-c", is_active=True)
        PriceListItem.objects.create(
            price_list=self.price_list,
            variant=self.variant,
            unit_price_ex_gst_cents=10000,
        )

        self.warehouse = Warehouse.objects.create(
            code="SYD1",
            name="Sydney DC",
            warehouse_type=Warehouse.WarehouseType.DISTRIBUTION,
            is_active=True,
        )
        InventoryLevel.objects.create(
            warehouse=self.warehouse,
            variant=self.variant,
            quantity_on_hand=150,
            quantity_reserved=0,
        )
        self.supplier = Supplier.objects.create(code="SUP-PHASEC-1", name="Phase C Supplier")

    def _create_customer_cart(self, qty: int = 2) -> Cart:
        cart = Cart.objects.create(customer=self.customer, currency_code="AUD")
        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=qty,
            unit_price_cents=10000,
        )
        return cart

    def _create_order_payload(self, cart_id: str) -> dict:
        return {
            "cart_id": cart_id,
            "billing_address": ADDRESS,
            "shipping_address": ADDRESS,
            "shipping_method_id": str(uuid.uuid4()),
            "payment_method": "card",
            "email": self.customer_user.email,
        }

    def test_customer_journey_register_login_browse_cart_checkout_pay_view_order(self):
        register = self.client.post(
            "/api/v1/auth/register/",
            {
                "email": "phasec-buyer@example.com",
                "password": "SecurePass123!",
                "password_confirm": "SecurePass123!",
                "first_name": "Phase",
                "last_name": "Buyer",
                "phone": "0400000000",
                "customer_type": "retail",
            },
            format="json",
        )
        self.assertEqual(register.status_code, status.HTTP_201_CREATED)

        login = self.client.post(
            "/api/v1/auth/login/",
            {"email": "phasec-buyer@example.com", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)

        products = self.client.get("/api/v1/products/", {"search": "drill"})
        self.assertEqual(products.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(products.data["data"]), 1)
        self.assertEqual(self.client.get("/api/v1/categories/").status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get("/api/v1/brands/").status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.customer_user)
        add_to_cart = self.client.post(
            "/api/v1/cart/items/",
            {"variant_id": str(self.variant.public_id), "quantity": 2},
            format="json",
        )
        self.assertEqual(add_to_cart.status_code, status.HTTP_201_CREATED)

        cart = self.client.get("/api/v1/cart/")
        self.assertEqual(cart.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(cart.data["items"]), 1)

        with patch("apps.payments.services.stripe.PaymentIntent.create") as mock_pi_create:
            mock_pi_create.return_value = MagicMock(
                id="pi_phasec_1",
                client_secret="cs_phasec_1",
                status="requires_payment_method",
            )
            checkout = self.client.post(
                "/api/v1/orders/",
                self._create_order_payload(cart.data["id"]),
                format="json",
            )
        self.assertEqual(checkout.status_code, status.HTTP_201_CREATED)
        order_id = checkout.data["id"]
        self.assertEqual(checkout.data["status"], "awaiting_payment")

        config = self.client.get("/api/v1/payments/config/")
        self.assertEqual(config.status_code, status.HTTP_200_OK)
        self.assertTrue(config.data["stripe_enabled"])

        with patch("apps.payments.services.PaymentService.construct_webhook_event") as mock_construct:
            mock_construct.return_value = MagicMock(
                id="evt_phasec_success_1",
                type="payment_intent.succeeded",
                data=MagicMock(object={"id": "pi_phasec_1", "status": "succeeded"}),
            )
            webhook = self.client.post(
                "/api/v1/payments/webhook/",
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="sig_phasec",
            )
        self.assertEqual(webhook.status_code, status.HTTP_200_OK)

        order_detail = self.client.get(f"/api/v1/orders/{order_id}/")
        self.assertEqual(order_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(order_detail.data["payment_status"], "paid")

    def test_operations_journey_trade_po_receive_ship_refund(self):
        org = Organization.objects.create(
            legal_name="Phase C Trade Co Pty Ltd",
            trading_name="Phase C Trade",
            abn="53004085616",
            email="trade-phasec@example.com",
            customer_segment=Organization.CustomerSegment.BUSINESS,
        )
        trade_customer_user = User.objects.create_user(
            email="trade-user@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        RoleService.assign_role(trade_customer_user, RoleSlug.TRADE_CUSTOMER)
        Customer.objects.create(
            user=trade_customer_user,
            customer_type="trade",
            organization=org,
            trade_account_status="pending",
        )
        application = TradeApplication.objects.create(organization=org, status="pending")

        self.client.force_authenticate(self.trade_reviewer)
        review = self.client.post(
            f"/api/v1/trade-accounts/admin/applications/{application.public_id}/review/",
            {"status": "approved", "credit_limit_cents": 500000},
            format="json",
        )
        self.assertEqual(review.status_code, status.HTTP_200_OK)
        self.assertEqual(review.data["status"], "approved")

        self.client.force_authenticate(self.manager)
        create_po = self.client.post(
            "/api/v1/suppliers/purchase-orders/",
            {
                "supplier_id": str(self.supplier.public_id),
                "warehouse_code": self.warehouse.code,
                "lines": [{"sku": self.variant.sku, "quantity": 12, "unit_cost_cents": 6500}],
            },
            format="json",
        )
        self.assertEqual(create_po.status_code, status.HTTP_201_CREATED)
        po_id = create_po.data["id"]

        submit_po = self.client.post(f"/api/v1/suppliers/purchase-orders/{po_id}/submit/")
        self.assertEqual(submit_po.status_code, status.HTTP_200_OK)
        confirm_po = self.client.post(f"/api/v1/suppliers/purchase-orders/{po_id}/confirm/")
        self.assertEqual(confirm_po.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.warehouse_user)
        receive_po = self.client.post(
            f"/api/v1/suppliers/purchase-orders/{po_id}/receive/",
            {
                "receipts": [
                    {
                        "line_id": confirm_po.data["lines"][0]["id"],
                        "quantity": 12,
                    }
                ]
            },
            format="json",
        )
        self.assertEqual(receive_po.status_code, status.HTTP_200_OK)
        self.assertIn(receive_po.data["status"], ["partial_received", "received"])

        self.client.force_authenticate(self.customer_user)
        cart = self._create_customer_cart(qty=1)
        with patch("apps.payments.services.stripe.PaymentIntent.create") as mock_pi_create:
            mock_pi_create.return_value = MagicMock(
                id="pi_phasec_ops_1",
                client_secret="cs_phasec_ops_1",
                status="requires_payment_method",
            )
            checkout = self.client.post(
                "/api/v1/orders/",
                self._create_order_payload(str(cart.public_id)),
                format="json",
            )
        self.assertEqual(checkout.status_code, status.HTTP_201_CREATED)
        order_id = checkout.data["id"]

        with patch("apps.payments.services.PaymentService.construct_webhook_event") as mock_construct:
            mock_construct.return_value = MagicMock(
                id="evt_phasec_success_2",
                type="payment_intent.succeeded",
                data=MagicMock(object={"id": "pi_phasec_ops_1", "status": "succeeded"}),
            )
            webhook = self.client.post(
                "/api/v1/payments/webhook/",
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="sig_phasec_ops",
            )
        self.assertEqual(webhook.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.manager)
        pack = self.client.post(f"/api/v1/orders/{order_id}/pack/")
        self.assertEqual(pack.status_code, status.HTTP_200_OK)
        ship = self.client.post(
            f"/api/v1/orders/{order_id}/ship/",
            {"carrier": "Australia Post", "tracking_number": "AP-PHASEC-1"},
            format="json",
        )
        self.assertEqual(ship.status_code, status.HTTP_200_OK)
        deliver = self.client.post(f"/api/v1/orders/{order_id}/deliver/")
        self.assertEqual(deliver.status_code, status.HTTP_200_OK)
        refund = self.client.post(
            f"/api/v1/orders/{order_id}/refund/",
            {"reason": "Pilot validation refund"},
            format="json",
        )
        self.assertEqual(refund.status_code, status.HTTP_200_OK)
        self.assertEqual(refund.data["status"], "refunded")

        reports = self.client.get("/api/v1/analytics/admin/reports/")
        self.assertEqual(reports.status_code, status.HTTP_200_OK)
        export = self.client.post(
            "/api/v1/analytics/admin/reports/export/",
            {"report_id": "sales", "format": "csv"},
            format="json",
        )
        self.assertEqual(export.status_code, status.HTTP_200_OK)
        self.assertIn("filename", export.data)
        self.assertIn("content", export.data)
