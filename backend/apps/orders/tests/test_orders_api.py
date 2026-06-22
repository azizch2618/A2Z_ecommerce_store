"""Order management API tests."""
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
from apps.customers.models import Customer
from apps.inventory.models import InventoryLevel, Warehouse
from apps.orders.models import Cart, CartItem, Order, Payment
from apps.orders.services import CartService, OrderService
from apps.pricing.models import PriceList, PriceListItem

User = get_user_model()

ADDRESS = {
    "line1": "1 George St",
    "suburb": "Sydney",
    "state": "NSW",
    "postcode": "2000",
    "country": "AU",
}


class OrderModuleTestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.user = User.objects.create_user(
            email="orderer@example.com",
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
        price_list = PriceList.objects.create(
            name="Retail",
            slug="retail",
            is_active=True,
        )
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
            "email": "orderer@example.com",
        }

    @override_settings(DEMO_AUTO_COMPLETE_PAYMENTS=False, STRIPE_SECRET_KEY="")
    def test_create_order_with_gst_totals(self):
        response = self.client.post(
            reverse("orders:order-list-create"),
            self._create_order_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "awaiting_payment")
        self.assertEqual(response.data["payment_status"], "pending")
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["unit_gst_cents"], 1000)
        self.assertEqual(response.data["items"][0]["gst_rate"], "0.1000")
        self.assertEqual(response.data["totals"]["subtotal_ex_gst_cents"], 20000)
        self.assertEqual(response.data["totals"]["gst_total_cents"], 2150)
        self.assertEqual(response.data["totals"]["shipping_ex_gst_cents"], 1500)
        self.assertEqual(response.data["totals"]["shipping_gst_cents"], 150)
        self.assertEqual(response.data["totals"]["total_inc_gst_cents"], 23650)
        self.assertIsNotNone(response.data["payment"])

        order = Order.objects.get(public_id=response.data["id"])
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(Payment.objects.filter(order=order).count(), 1)
        self.assertFalse(self.cart.items.exists())

    def test_order_history_and_detail(self):
        order = OrderService.create_from_cart(
            cart=self.cart,
            customer=self.customer,
            billing_address=ADDRESS,
            shipping_method_id=str(uuid.uuid4()),
            payment_method="card",
            email=self.user.email,
        )

        list_response = self.client.get(reverse("orders:order-list-create"))
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data["data"]), 1)
        self.assertEqual(list_response.data["data"][0]["order_number"], order.order_number)

        detail_response = self.client.get(
            reverse("orders:order-detail", kwargs={"public_id": order.public_id}),
        )
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["order_number"], order.order_number)
        self.assertIn("billing_address", detail_response.data)
        self.assertIn("totals", detail_response.data)

    def test_track_order_guest(self):
        order = OrderService.create_from_cart(
            cart=self.cart,
            customer=self.customer,
            billing_address=ADDRESS,
            shipping_method_id=str(uuid.uuid4()),
            payment_method="card",
            email=self.user.email,
        )
        OrderService.mark_paid(order)
        OrderService.mark_packed(order)
        OrderService.mark_shipped(
            order,
            carrier="Australia Post",
            tracking_number="AP123456",
            tracking_url="https://auspost.com.au/track/AP123456",
        )

        self.client.force_authenticate(user=None)
        track_response = self.client.post(
            reverse("orders:order-track"),
            {"order_number": order.order_number, "email": self.user.email},
            format="json",
        )
        self.assertEqual(track_response.status_code, status.HTTP_200_OK)
        self.assertEqual(track_response.data["status"], "shipped")
        self.assertEqual(len(track_response.data["shipments"]), 1)
        self.assertEqual(track_response.data["shipments"][0]["tracking_number"], "AP123456")

    @override_settings(DEMO_AUTO_COMPLETE_PAYMENTS=True, STRIPE_SECRET_KEY="")
    def test_order_status_workflow(self):
        cart = Cart.objects.create(customer=self.customer, currency_code="AUD")
        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=1,
            unit_price_cents=10000,
        )
        order = OrderService.create_from_cart(
            cart=cart,
            customer=self.customer,
            billing_address=ADDRESS,
            shipping_method_id=str(uuid.uuid4()),
            payment_method="card",
        )

        self.assertEqual(order.status, Order.Status.PAID)
        OrderService.mark_packed(order)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.PACKED)

        OrderService.mark_shipped(order, tracking_number="TRK-99")
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.SHIPPED)

        OrderService.mark_delivered(order)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.DELIVERED)


class StaffOrderAPITestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.cs_user = User.objects.create_user(
            email="cs@example.com",
            password="SecurePass123!",
            is_staff=True,
        )
        RoleService.assign_role(self.cs_user, RoleSlug.CUSTOMER_SERVICE)

        self.customer_user = User.objects.create_user(
            email="buyer@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        self.customer = Customer.objects.create(
            user=self.customer_user,
            customer_type="retail",
        )
        RoleService.assign_role(self.customer_user, RoleSlug.CUSTOMER)

        brand = Brand.objects.create(name="Makita", slug="makita")
        product = Product.objects.create(
            brand=brand,
            name="Drill",
            slug="drill-staff",
            is_active=True,
        )
        variant = ProductVariant.objects.create(
            product=product,
            sku="DRL-STAFF",
            is_default=True,
            is_active=True,
        )
        price_list = PriceList.objects.create(
            name="Retail",
            slug="retail-staff",
            is_active=True,
        )
        PriceListItem.objects.create(
            price_list=price_list,
            variant=variant,
            unit_price_ex_gst_cents=5000,
        )
        warehouse = Warehouse.objects.create(code="SYD1", name="Sydney", is_active=True)
        InventoryLevel.objects.create(
            warehouse=warehouse,
            variant=variant,
            quantity_on_hand=50,
            quantity_reserved=0,
        )
        cart = Cart.objects.create(customer=self.customer, currency_code="AUD")
        CartItem.objects.create(cart=cart, variant=variant, quantity=1, unit_price_cents=5000)
        self.order = OrderService.create_from_cart(
            cart=cart,
            customer=self.customer,
            billing_address=ADDRESS,
            shipping_method_id=str(uuid.uuid4()),
            payment_method="card",
            email=self.customer_user.email,
        )
        OrderService.mark_paid(self.order)

    def test_staff_lists_all_orders(self):
        self.client.force_authenticate(self.cs_user)
        response = self.client.get(reverse("orders:order-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

    def test_staff_pack_ship_deliver_workflow(self):
        self.client.force_authenticate(self.cs_user)
        po_id = self.order.public_id

        detail = self.client.get(reverse("orders:order-detail", kwargs={"public_id": po_id}))
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["order_number"], self.order.order_number)
        self.assertIn("customer_id", detail.data)
        self.assertIn("items", detail.data)
        self.assertIn("totals", detail.data)

        invoice = self.client.get(reverse("orders:order-invoice", kwargs={"public_id": po_id}))
        self.assertEqual(invoice.status_code, status.HTTP_200_OK)
        self.assertEqual(invoice["Content-Type"], "application/pdf")

        pack = self.client.post(reverse("orders:order-pack", kwargs={"public_id": po_id}))
        self.assertEqual(pack.status_code, status.HTTP_200_OK)
        self.assertEqual(pack.data["status"], "packed")

        ship = self.client.post(
            reverse("orders:order-ship", kwargs={"public_id": po_id}),
            {"carrier": "Australia Post", "tracking_number": "AP999"},
            format="json",
        )
        self.assertEqual(ship.status_code, status.HTTP_200_OK)
        self.assertEqual(ship.data["status"], "shipped")

        deliver = self.client.post(reverse("orders:order-deliver", kwargs={"public_id": po_id}))
        self.assertEqual(deliver.status_code, status.HTTP_200_OK)
        self.assertEqual(deliver.data["status"], "delivered")

    def test_customer_cannot_pack_order(self):
        self.client.force_authenticate(self.customer_user)
        response = self.client.post(
            reverse("orders:order-pack", kwargs={"public_id": self.order.public_id}),
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CartMergeAPITestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.user = User.objects.create_user(
            email="merger@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        self.customer = Customer.objects.create(user=self.user, customer_type="retail")
        RoleService.assign_role(self.user, RoleSlug.CUSTOMER)

        brand = Brand.objects.create(name="Makita", slug="makita-merge")
        product = Product.objects.create(
            brand=brand,
            name="Impact Driver",
            slug="impact-driver",
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="IMP-001",
            is_default=True,
            is_active=True,
        )
        price_list = PriceList.objects.create(
            name="Retail",
            slug="retail-merge",
            is_active=True,
        )
        PriceListItem.objects.create(
            price_list=price_list,
            variant=self.variant,
            unit_price_ex_gst_cents=15000,
        )

        self.session_key = "guest-session-merge-001"
        self.guest_cart = Cart.objects.create(
            session_key=self.session_key,
            currency_code="AUD",
        )
        CartItem.objects.create(
            cart=self.guest_cart,
            variant=self.variant,
            quantity=2,
            unit_price_cents=15000,
        )

        self.client.force_authenticate(self.user)

    def test_merge_guest_cart_into_customer_cart(self):
        response = self.client.post(
            reverse("orders_cart:cart-merge"),
            {"session_key": self.session_key},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["quantity"], 2)
        self.assertFalse(Cart.objects.filter(session_key=self.session_key).exists())

        customer_cart = Cart.objects.get(customer=self.customer)
        self.assertEqual(customer_cart.items.count(), 1)
        self.assertEqual(customer_cart.items.first().quantity, 2)

    def test_merge_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("orders_cart:cart-merge"),
            {"session_key": self.session_key},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CartMergeAPITestCase(APITestCase):
    def setUp(self):
        RoleService.ensure_system_roles()
        self.user = User.objects.create_user(
            email="merger@example.com",
            password="SecurePass123!",
            email_verified_at=timezone.now(),
        )
        self.customer = Customer.objects.create(user=self.user, customer_type="retail")
        RoleService.assign_role(self.user, RoleSlug.CUSTOMER)

        brand = Brand.objects.create(name="Makita", slug="makita-merge")
        product = Product.objects.create(
            brand=brand,
            name="Impact Driver",
            slug="impact-driver",
            is_active=True,
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            sku="IMP-001",
            is_default=True,
            is_active=True,
        )
        price_list = PriceList.objects.create(
            name="Retail",
            slug="retail-merge",
            is_active=True,
        )
        PriceListItem.objects.create(
            price_list=price_list,
            variant=self.variant,
            unit_price_ex_gst_cents=15000,
        )

        self.session_key = "guest-session-merge-001"
        self.guest_cart = Cart.objects.create(
            session_key=self.session_key,
            currency_code="AUD",
        )
        CartItem.objects.create(
            cart=self.guest_cart,
            variant=self.variant,
            quantity=2,
            unit_price_cents=15000,
        )

        self.client.force_authenticate(self.user)

    def test_merge_guest_cart_into_customer_cart(self):
        response = self.client.post(
            reverse("orders_cart:cart-merge"),
            {"session_key": self.session_key},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["quantity"], 2)
        self.assertFalse(Cart.objects.filter(session_key=self.session_key).exists())

        customer_cart = Cart.objects.get(customer=self.customer)
        self.assertEqual(customer_cart.items.count(), 1)
        self.assertEqual(customer_cart.items.first().quantity, 2)

    def test_merge_requires_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            reverse("orders_cart:cart-merge"),
            {"session_key": self.session_key},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
