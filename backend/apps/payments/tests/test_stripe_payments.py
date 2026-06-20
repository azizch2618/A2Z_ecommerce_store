"""Stripe payment processing tests."""
import json
import uuid
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.constants import RoleSlug
from apps.accounts.services import RoleService
from apps.catalog.models import Brand, Product, ProductVariant
from apps.customers.models import Customer
from apps.inventory.models import InventoryLevel, InventoryTransaction, Warehouse
from apps.orders.models import Cart, CartItem, Order, Payment
from apps.orders.services import OrderService
from apps.payments.models import StripeWebhookEvent
from apps.pricing.models import PriceList, PriceListItem

User = get_user_model()

ADDRESS = {
    "line1": "1 George St",
    "suburb": "Sydney",
    "state": "NSW",
    "postcode": "2000",
    "country": "AU",
}

STRIPE_SETTINGS = {
    "STRIPE_SECRET_KEY": "sk_test_fake",
    "STRIPE_PUBLISHABLE_KEY": "pk_test_fake",
    "STRIPE_WEBHOOK_SECRET": "whsec_test_fake",
    "DEMO_AUTO_COMPLETE_PAYMENTS": False,
}


@override_settings(**STRIPE_SETTINGS)
class StripePaymentTestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.user = User.objects.create_user(
            email="payer@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        self.customer = Customer.objects.create(user=self.user, customer_type="retail")
        RoleService.assign_role(self.user, RoleSlug.CUSTOMER)

        brand = Brand.objects.create(name="Makita", slug="makita")
        product = Product.objects.create(
            brand=brand,
            name="Drill",
            slug="drill",
            is_active=True,
        )
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

        self.warehouse = Warehouse.objects.create(
            code="SYD1",
            name="Sydney",
            is_active=True,
        )
        InventoryLevel.objects.create(
            warehouse=self.warehouse,
            variant=self.variant,
            quantity_on_hand=10,
            quantity_reserved=0,
        )

        self.cart = Cart.objects.create(customer=self.customer, currency_code="AUD")
        CartItem.objects.create(
            cart=self.cart,
            variant=self.variant,
            quantity=2,
            unit_price_cents=10000,
        )

        self.client.force_authenticate(self.user)

    def _create_order_payload(self):
        return {
            "cart_id": str(self.cart.public_id),
            "billing_address": ADDRESS,
            "shipping_address": ADDRESS,
            "shipping_method_id": str(uuid.uuid4()),
            "payment_method": "card",
            "email": "payer@example.com",
        }

    @patch("apps.payments.services.stripe.PaymentIntent.create")
    def test_successful_payment_webhook_marks_paid_and_deducts_inventory(self, mock_pi_create):
        mock_pi_create.return_value = MagicMock(
            id="pi_test_success",
            client_secret="cs_test_secret",
            status="requires_payment_method",
        )

        response = self.client.post(
            reverse("orders:order-list-create"),
            self._create_order_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "awaiting_payment")
        self.assertEqual(response.data["payment"]["client_secret"], "cs_test_secret")

        order = Order.objects.get(public_id=response.data["id"])
        payment = Payment.objects.get(order=order)
        self.assertEqual(payment.gateway_payment_id, "pi_test_success")

        initial_stock = InventoryLevel.objects.get(
            warehouse=self.warehouse,
            variant=self.variant,
        ).quantity_on_hand

        with patch(
            "apps.payments.services.PaymentService.construct_webhook_event"
        ) as mock_construct:
            mock_construct.return_value = MagicMock(
                id="evt_success_1",
                type="payment_intent.succeeded",
                data=MagicMock(
                    object={
                        "id": "pi_test_success",
                        "status": "succeeded",
                    }
                ),
            )
            webhook_response = self.client.post(
                reverse("payments:stripe-webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="sig_test",
            )

        self.assertEqual(webhook_response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(order.payment_status, Order.PaymentStatus.PAID)
        self.assertEqual(payment.status, Payment.Status.PAID)
        self.assertTrue(
            StripeWebhookEvent.objects.filter(stripe_event_id="evt_success_1").exists()
        )
        self.assertEqual(len(mail.outbox), 1)

        level = InventoryLevel.objects.get(warehouse=self.warehouse, variant=self.variant)
        self.assertEqual(level.quantity_on_hand, initial_stock - 2)
        self.assertTrue(
            InventoryTransaction.objects.filter(
                reference_type="order",
                reference_id=order.id,
                transaction_type=InventoryTransaction.TransactionType.SALE,
            ).exists()
        )

    @patch("apps.payments.services.stripe.PaymentIntent.create")
    def test_failed_payment_webhook(self, mock_pi_create):
        mock_pi_create.return_value = MagicMock(
            id="pi_test_fail",
            client_secret="cs_test_fail",
            status="requires_payment_method",
        )

        response = self.client.post(
            reverse("orders:order-list-create"),
            self._create_order_payload(),
            format="json",
        )
        order = Order.objects.get(public_id=response.data["id"])

        with patch(
            "apps.payments.services.PaymentService.construct_webhook_event"
        ) as mock_construct:
            mock_construct.return_value = MagicMock(
                id="evt_fail_1",
                type="payment_intent.payment_failed",
                data=MagicMock(
                    object={
                        "id": "pi_test_fail",
                        "status": "requires_payment_method",
                    }
                ),
            )
            webhook_response = self.client.post(
                reverse("payments:stripe-webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="sig_test",
            )

        self.assertEqual(webhook_response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, Order.PaymentStatus.FAILED)
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertFalse(
            InventoryTransaction.objects.filter(
                reference_type="order",
                reference_id=order.id,
            ).exists()
        )

    @patch("apps.payments.services.stripe.PaymentIntent.create")
    def test_duplicate_webhook_is_idempotent(self, mock_pi_create):
        mock_pi_create.return_value = MagicMock(
            id="pi_test_dup",
            client_secret="cs_test_dup",
            status="requires_payment_method",
        )

        response = self.client.post(
            reverse("orders:order-list-create"),
            self._create_order_payload(),
            format="json",
        )
        order = Order.objects.get(public_id=response.data["id"])
        initial_stock = InventoryLevel.objects.get(
            warehouse=self.warehouse,
            variant=self.variant,
        ).quantity_on_hand

        event = MagicMock(
            id="evt_dup_1",
            type="payment_intent.succeeded",
            data=MagicMock(
                object={
                    "id": "pi_test_dup",
                    "status": "succeeded",
                }
            ),
        )

        with patch(
            "apps.payments.services.PaymentService.construct_webhook_event",
            return_value=event,
        ):
            self.client.post(
                reverse("payments:stripe-webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="sig_test",
            )
            self.client.post(
                reverse("payments:stripe-webhook"),
                data=b"{}",
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="sig_test",
            )

        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertEqual(StripeWebhookEvent.objects.filter(stripe_event_id="evt_dup_1").count(), 1)
        self.assertEqual(
            InventoryTransaction.objects.filter(
                reference_type="order",
                reference_id=order.id,
            ).count(),
            1,
        )
        level = InventoryLevel.objects.get(warehouse=self.warehouse, variant=self.variant)
        self.assertEqual(level.quantity_on_hand, initial_stock - 2)

    @patch("apps.payments.services.stripe.PaymentIntent.create")
    def test_inventory_deduction_only_after_webhook(self, mock_pi_create):
        mock_pi_create.return_value = MagicMock(
            id="pi_test_inv",
            client_secret="cs_test_inv",
            status="requires_payment_method",
        )

        response = self.client.post(
            reverse("orders:order-list-create"),
            self._create_order_payload(),
            format="json",
        )
        order = Order.objects.get(public_id=response.data["id"])
        self.assertEqual(order.status, Order.Status.AWAITING_PAYMENT)
        self.assertFalse(
            InventoryTransaction.objects.filter(
                reference_type="order",
                reference_id=order.id,
            ).exists()
        )

    def test_insufficient_stock_blocks_order_creation(self):
        level = InventoryLevel.objects.get(warehouse=self.warehouse, variant=self.variant)
        level.quantity_on_hand = 1
        level.save(update_fields=["quantity_on_hand", "updated_at"])

        response = self.client.post(
            reverse("orders:order-list-create"),
            self._create_order_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_webhook_rejects_missing_signature(self):
        response = self.client.post(
            reverse("payments:stripe-webhook"),
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
