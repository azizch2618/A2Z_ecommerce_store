"""Order and cart business logic with Australian GST."""
from __future__ import annotations

import uuid
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import Count, F, QuerySet
from django.utils import timezone

from apps.catalog.models import ProductVariant
from apps.catalog.pricing_helpers import get_variant_unit_price_cents
from apps.inventory.models import InventoryTransaction, Warehouse
from apps.inventory.services import InventoryService
from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.customers.models import Customer
from apps.orders.models import Cart, CartItem, Order, OrderItem, Payment, Shipment, Wishlist, WishlistItem
from apps.orders.emails import send_order_confirmation_email
from apps.pricing.services import PricingService


class CartService:
    @staticmethod
    def get_or_create_cart(*, customer: Customer | None = None, session_key: str | None = None) -> Cart:
        if customer:
            cart, _ = Cart.objects.get_or_create(
                customer=customer,
                defaults={"currency_code": "AUD"},
            )
            return cart
        if session_key:
            cart, _ = Cart.objects.get_or_create(
                session_key=session_key,
                defaults={"currency_code": "AUD"},
            )
            return cart
        raise ValueError("Customer or session_key required.")

    @staticmethod
    @transaction.atomic
    def add_item(cart: Cart, variant_public_id, quantity: int) -> Cart:
        try:
            variant = ProductVariant.objects.select_related("product").get(
                public_id=variant_public_id,
            )
        except ProductVariant.DoesNotExist as exc:
            raise NotFoundError("Variant not found.") from exc
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                "quantity": quantity,
                "unit_price_cents": get_variant_unit_price_cents(variant),
            },
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity", "updated_at"])
        return cart

    @staticmethod
    @transaction.atomic
    def update_item_quantity(cart: Cart, item_public_id, quantity: int) -> Cart:
        try:
            item = cart.items.select_related("variant").get(public_id=item_public_id)
        except CartItem.DoesNotExist as exc:
            raise NotFoundError("Cart item not found.") from exc
        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save(update_fields=["quantity", "updated_at"])
        return cart

    @staticmethod
    @transaction.atomic
    def remove_item(cart: Cart, item_public_id) -> Cart:
        cart.items.filter(public_id=item_public_id).delete()
        return cart

    @staticmethod
    @transaction.atomic
    def clear(cart: Cart) -> Cart:
        cart.items.all().delete()
        return cart

    @staticmethod
    @transaction.atomic
    def merge_guest_cart(*, customer: Customer, session_key: str) -> Cart:
        """Merge a guest session cart into the authenticated customer's cart."""
        customer_cart = CartService.get_or_create_cart(customer=customer)
        if not session_key:
            return customer_cart

        guest_cart = (
            Cart.objects.filter(session_key=session_key, customer__isnull=True)
            .prefetch_related("items__variant")
            .first()
        )
        if not guest_cart or guest_cart.pk == customer_cart.pk:
            return customer_cart

        for guest_item in guest_cart.items.all():
            item, created = CartItem.objects.get_or_create(
                cart=customer_cart,
                variant=guest_item.variant,
                defaults={
                    "quantity": guest_item.quantity,
                    "unit_price_cents": guest_item.unit_price_cents,
                },
            )
            if not created:
                item.quantity += guest_item.quantity
                item.save(update_fields=["quantity", "updated_at"])

        guest_cart.items.all().delete()
        guest_cart.delete()
        return customer_cart

    @staticmethod
    def build_cart_totals(cart: Cart) -> dict[str, int | str]:
        subtotal_ex = 0
        gst_total = 0
        for item in cart.items.select_related("variant"):
            unit_ex = OrderService._resolve_cart_item_price(item)
            unit_gst = PricingService.calculate_gst(unit_ex)
            subtotal_ex += unit_ex * item.quantity
            gst_total += unit_gst * item.quantity
        return {
            "subtotal_ex_gst_cents": subtotal_ex,
            "gst_cents": gst_total,
            "discount_cents": 0,
            "total_inc_gst_cents": subtotal_ex + gst_total,
            "currency_code": "AUD",
        }


class WishlistService:
    @staticmethod
    def get_or_create_wishlist(customer: Customer) -> Wishlist:
        wishlist, _ = Wishlist.objects.get_or_create(
            customer=customer,
            is_default=True,
            defaults={"name": "Default"},
        )
        return wishlist

    @staticmethod
    @transaction.atomic
    def add_item(wishlist: Wishlist, variant_public_id, quantity: int = 1) -> Wishlist:
        try:
            variant = ProductVariant.objects.select_related("product", "product__brand").get(
                public_id=variant_public_id,
            )
        except ProductVariant.DoesNotExist as exc:
            raise NotFoundError("Variant not found.") from exc
        item, created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            variant=variant,
            defaults={"desired_quantity": quantity},
        )
        if not created:
            item.desired_quantity = quantity
            item.save(update_fields=["desired_quantity", "updated_at"])
        return wishlist

    @staticmethod
    @transaction.atomic
    def remove_item(wishlist: Wishlist, item_public_id) -> Wishlist:
        wishlist.items.filter(public_id=item_public_id).delete()
        return wishlist

    @staticmethod
    @transaction.atomic
    def remove_by_variant(wishlist: Wishlist, variant_public_id) -> Wishlist:
        wishlist.items.filter(variant__public_id=variant_public_id).delete()
        return wishlist


class OrderService:
    DEFAULT_SHIPPING_EX_GST_CENTS = 1500

    @staticmethod
    def generate_order_number() -> str:
        today = timezone.localdate().strftime("%Y%m%d")
        count = Order.objects.filter(order_number__startswith=f"A2Z-{today}").count() + 1
        return f"A2Z-{today}-{count:04d}"

    @staticmethod
    def staff_orders_queryset() -> QuerySet[Order]:
        return (
            Order.objects.select_related("customer", "customer__user", "organization")
            .annotate(item_count=Count("items"))
            .prefetch_related("items", "payments", "shipments")
            .order_by("-placed_at", "-created_at")
        )

    @staticmethod
    def get_by_public_id(public_id) -> Order:
        try:
            return OrderService.staff_orders_queryset().get(public_id=public_id)
        except Order.DoesNotExist as exc:
            raise NotFoundError("Order not found.") from exc

    @staticmethod
    def customer_orders_queryset(customer: Customer) -> QuerySet[Order]:
        return (
            Order.objects.filter(customer=customer)
            .annotate(item_count=Count("items"))
            .prefetch_related("items", "payments", "shipments")
            .order_by("-placed_at", "-created_at")
        )

    @staticmethod
    def _resolve_cart_item_price(cart_item: CartItem) -> int:
        if cart_item.unit_price_cents:
            return int(cart_item.unit_price_cents)
        return get_variant_unit_price_cents(cart_item.variant)

    @staticmethod
    def _normalize_address(address: dict[str, Any]) -> dict[str, Any]:
        return {
            "line1": address.get("line1", ""),
            "line2": address.get("line2", ""),
            "suburb": address.get("suburb", ""),
            "state": address.get("state", ""),
            "postcode": address.get("postcode", ""),
            "country": address.get("country", "AU"),
            "label": address.get("label", ""),
        }

    @staticmethod
    @transaction.atomic
    def create_from_cart(
        *,
        cart: Cart,
        customer: Customer,
        billing_address: dict[str, Any],
        shipping_address: dict[str, Any] | None = None,
        shipping_method_id: str | None = None,
        payment_method: str = "card",
        email: str | None = None,
        po_number: str = "",
        customer_notes: str = "",
        shipping_ex_gst_cents: int | None = None,
    ) -> Order:
        if not cart.items.exists():
            raise ConflictError("Cart is empty.")

        InventoryService.validate_cart_availability(cart)

        shipping_address = shipping_address or billing_address
        shipping_ex = (
            shipping_ex_gst_cents
            if shipping_ex_gst_cents is not None
            else OrderService.DEFAULT_SHIPPING_EX_GST_CENTS
        )
        shipping_gst = PricingService.calculate_gst(shipping_ex)

        initial_status = Order.Status.PENDING
        if payment_method == "card":
            initial_status = Order.Status.AWAITING_PAYMENT

        order = Order.objects.create(
            order_number=OrderService.generate_order_number(),
            customer=customer,
            organization=customer.organization,
            status=initial_status,
            payment_status=Order.PaymentStatus.PENDING,
            currency_code="AUD",
            guest_email=email or "",
            billing_address=OrderService._normalize_address(billing_address),
            shipping_address=OrderService._normalize_address(shipping_address),
            shipping_method={
                "id": shipping_method_id or "",
                "name": "Standard Delivery",
                "carrier": "Australia Post",
            },
            payment_method=payment_method,
            po_number=po_number,
            customer_notes=customer_notes,
            placed_at=timezone.now(),
            shipping_ex_gst_cents=shipping_ex,
            shipping_gst_cents=shipping_gst,
        )

        subtotal_ex = 0
        gst_total = 0
        for cart_item in cart.items.select_related("variant", "variant__product"):
            unit_ex = OrderService._resolve_cart_item_price(cart_item)
            unit_gst = PricingService.calculate_gst(unit_ex)
            line_ex = unit_ex * cart_item.quantity
            line_gst = unit_gst * cart_item.quantity
            OrderItem.objects.create(
                order=order,
                variant=cart_item.variant,
                sku=cart_item.variant.sku,
                product_name=cart_item.variant.product.name,
                variant_name=cart_item.variant.name,
                quantity=cart_item.quantity,
                unit_price_ex_gst_cents=unit_ex,
                unit_gst_cents=unit_gst,
                gst_rate=PricingService.GST_RATE,
                line_total_ex_gst_cents=line_ex,
                line_gst_cents=line_gst,
                line_total_inc_gst_cents=line_ex + line_gst,
            )
            subtotal_ex += line_ex
            gst_total += line_gst

        order.subtotal_ex_gst_cents = subtotal_ex
        order.gst_total_cents = gst_total + shipping_gst
        order.total_inc_gst_cents = subtotal_ex + gst_total + shipping_ex + shipping_gst
        order.save(
            update_fields=[
                "subtotal_ex_gst_cents",
                "gst_total_cents",
                "total_inc_gst_cents",
                "updated_at",
            ]
        )

        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            status=Payment.Status.PENDING,
            amount_cents=order.total_inc_gst_cents,
            gst_cents=order.gst_total_cents,
            currency_code=order.currency_code,
            idempotency_key=f"pay-{order.public_id}-{uuid.uuid4().hex[:12]}",
        )

        if payment_method == "trade_credit":
            from apps.trade_accounts.trade_credit import TradeCreditService

            trade_account = TradeCreditService.get_approved_account_for_customer(customer)
            if not trade_account:
                raise BusinessRuleError(
                    "An approved trade account is required for trade credit payment."
                )
            TradeCreditService.validate_credit_for_order(
                trade_account=trade_account,
                order=order,
            )
            order.trade_account = trade_account
            order.save(update_fields=["trade_account", "updated_at"])
            OrderService.mark_paid(order, payment=payment)
            if customer.user_id:
                TradeCreditService.authorize_and_charge(
                    trade_account=trade_account,
                    order=order,
                    user=customer.user,
                )
            send_order_confirmation_email(order)
        elif payment_method == "card":
            from apps.payments.services import PaymentService

            if PaymentService.is_stripe_configured():
                PaymentService.create_payment_intent_for_order(order=order, payment=payment)
            elif getattr(settings, "DEMO_AUTO_COMPLETE_PAYMENTS", False):
                OrderService.mark_paid(order, payment=payment)
                send_order_confirmation_email(order)

        cart.items.all().delete()
        Customer.objects.filter(pk=customer.pk).update(
            total_orders=F("total_orders") + 1,
            total_spent_cents=F("total_spent_cents") + order.total_inc_gst_cents,
        )
        return order

    @staticmethod
    @transaction.atomic
    def mark_paid(order: Order, *, payment: Payment | None = None) -> Order:
        if order.payment_status == Order.PaymentStatus.PAID:
            return order

        now = timezone.now()
        order.status = Order.Status.PAID
        order.payment_status = Order.PaymentStatus.PAID
        order.paid_at = now
        order.save(update_fields=["status", "payment_status", "paid_at", "updated_at"])

        if payment:
            payment.status = Payment.Status.PAID
            payment.paid_at = now
            payment.save(update_fields=["status", "paid_at", "updated_at"])

        InventoryService.validate_order_availability(order)
        OrderService._deduct_inventory_for_order(order)
        return order

    @staticmethod
    @transaction.atomic
    def mark_payment_failed(order: Order, *, payment: Payment | None = None) -> Order:
        if order.payment_status == Order.PaymentStatus.PAID:
            return order

        order.payment_status = Order.PaymentStatus.FAILED
        if order.status == Order.Status.AWAITING_PAYMENT:
            order.status = Order.Status.PENDING
        order.save(update_fields=["status", "payment_status", "updated_at"])

        if payment:
            payment.status = Payment.Status.FAILED
            payment.save(update_fields=["status", "updated_at"])
        return order

    @staticmethod
    def _deduct_inventory_for_order(order: Order) -> None:
        warehouse = Warehouse.objects.filter(
            code=InventoryService.DEFAULT_FULFILMENT_WAREHOUSE,
            is_active=True,
        ).first()
        if not warehouse:
            raise BusinessRuleError("Fulfilment warehouse is not configured.")
        for item in order.items.select_related("variant"):
            existing = InventoryTransaction.objects.filter(
                reference_type="order",
                reference_id=order.id,
                variant=item.variant,
                transaction_type=InventoryTransaction.TransactionType.SALE,
            ).exists()
            if existing:
                continue
            InventoryService.stock_out(
                sku=item.sku,
                warehouse_code=warehouse.code,
                quantity=item.quantity,
                transaction_type=InventoryTransaction.TransactionType.SALE,
                reference_type="order",
                reference_id=order.id,
                sale_price_cents=item.unit_price_ex_gst_cents,
                notes=f"Order {order.order_number}",
            )

    @staticmethod
    @transaction.atomic
    def mark_packed(order: Order) -> Order:
        if order.status not in {Order.Status.PAID, Order.Status.PACKED}:
            raise BusinessRuleError("Order must be paid before packing.")
        order.status = Order.Status.PACKED
        order.fulfilment_status = "packed"
        order.packed_at = timezone.now()
        order.save(update_fields=["status", "fulfilment_status", "packed_at", "updated_at"])
        return order

    @staticmethod
    @transaction.atomic
    def mark_shipped(
        order: Order,
        *,
        carrier: str = "",
        tracking_number: str = "",
        tracking_url: str = "",
    ) -> Shipment:
        if order.status not in {Order.Status.PAID, Order.Status.PACKED, Order.Status.SHIPPED}:
            raise BusinessRuleError("Order cannot be shipped in its current state.")

        now = timezone.now()
        shipment, created = Shipment.objects.update_or_create(
            order=order,
            defaults={
                "carrier": carrier,
                "tracking_number": tracking_number,
                "tracking_url": tracking_url,
                "status": Shipment.Status.SHIPPED,
                "shipped_at": now,
            },
        )

        order.status = Order.Status.SHIPPED
        order.fulfilment_status = "shipped"
        order.shipped_at = now
        order.save(update_fields=["status", "fulfilment_status", "shipped_at", "updated_at"])
        return shipment

    @staticmethod
    @transaction.atomic
    def mark_delivered(order: Order) -> Order:
        now = timezone.now()
        order.status = Order.Status.DELIVERED
        order.fulfilment_status = "delivered"
        order.delivered_at = now
        order.save(update_fields=["status", "fulfilment_status", "delivered_at", "updated_at"])

        for shipment in order.shipments.all():
            shipment.status = Shipment.Status.DELIVERED
            shipment.delivered_at = now
            shipment.save(update_fields=["status", "delivered_at", "updated_at"])
        return order

    @staticmethod
    @transaction.atomic
    def cancel_order(order: Order, *, reason: str = "") -> Order:
        if order.status in {Order.Status.SHIPPED, Order.Status.DELIVERED}:
            raise BusinessRuleError("Shipped or delivered orders cannot be cancelled.")
        order.status = Order.Status.CANCELLED
        order.payment_status = (
            Order.PaymentStatus.REFUNDED
            if order.payment_status == Order.PaymentStatus.PAID
            else order.payment_status
        )
        order.cancelled_at = timezone.now()
        if reason:
            order.customer_notes = f"{order.customer_notes}\nCancelled: {reason}".strip()
        order.save(
            update_fields=["status", "payment_status", "cancelled_at", "customer_notes", "updated_at"]
        )
        return order

    @staticmethod
    @transaction.atomic
    def refund_order(order: Order, *, reason: str = "", user=None) -> Order:
        if order.status not in {
            Order.Status.PAID,
            Order.Status.PACKED,
            Order.Status.SHIPPED,
            Order.Status.DELIVERED,
            Order.Status.CANCELLED,
        }:
            raise BusinessRuleError("Order cannot be refunded in its current state.")
        if order.status == Order.Status.REFUNDED:
            raise ConflictError("Order is already refunded.")

        order.status = Order.Status.REFUNDED
        order.payment_status = Order.PaymentStatus.REFUNDED
        if reason:
            order.customer_notes = f"{order.customer_notes}\nRefunded: {reason}".strip()
        order.save(
            update_fields=["status", "payment_status", "customer_notes", "updated_at"]
        )

        from apps.core.audit import log_operation
        from apps.core.models import OperationalAuditLog

        if user:
            log_operation(
                user=user,
                module=OperationalAuditLog.Module.ORDERS,
                action="refund",
                resource_type="order",
                resource_id=order.public_id,
                details={"order_number": order.order_number, "reason": reason},
            )
        return order

    @staticmethod
    def track_order(*, order_number: str, email: str) -> Order:
        try:
            order = Order.objects.prefetch_related("items", "shipments", "payments").get(
                order_number=order_number,
            )
        except Order.DoesNotExist as exc:
            raise NotFoundError("Order not found.") from exc

        customer_email = ""
        if order.customer.user_id:
            customer_email = (order.customer.user.email or "").lower()
        guest_email = (order.guest_email or "").lower()
        if email.lower() not in {customer_email, guest_email}:
            raise NotFoundError("Order not found.")

        return order

    @staticmethod
    def build_totals(order: Order) -> dict:
        return {
            "subtotal_ex_gst_cents": order.subtotal_ex_gst_cents,
            "gst_total_cents": order.gst_total_cents,
            "shipping_ex_gst_cents": order.shipping_ex_gst_cents,
            "shipping_gst_cents": order.shipping_gst_cents,
            "discount_cents": order.discount_cents,
            "total_inc_gst_cents": order.total_inc_gst_cents,
            "currency_code": order.currency_code,
        }
