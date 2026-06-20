"""Stripe Payment Intent service — server-side payment processing."""
from __future__ import annotations

import logging
from typing import Any

import stripe
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.inventory.services import InventoryService
from apps.orders.emails import send_order_confirmation_email
from apps.orders.models import Order, Payment
from apps.orders.services import OrderService
from apps.payments.models import StripeWebhookEvent

logger = logging.getLogger(__name__)


class PaymentService:
    @staticmethod
    def is_stripe_configured() -> bool:
        return bool(settings.STRIPE_SECRET_KEY)

    @staticmethod
    def _configure_stripe() -> None:
        if not PaymentService.is_stripe_configured():
            raise BusinessRuleError("Stripe is not configured.")
        stripe.api_key = settings.STRIPE_SECRET_KEY

    @staticmethod
    def create_payment_intent_for_order(*, order: Order, payment: Payment) -> Payment:
        """Create a Stripe PaymentIntent for a card order awaiting payment."""
        PaymentService._configure_stripe()

        intent = stripe.PaymentIntent.create(
            amount=payment.amount_cents,
            currency=payment.currency_code.lower(),
            automatic_payment_methods={"enabled": True},
            metadata={
                "order_public_id": str(order.public_id),
                "order_number": order.order_number,
                "payment_public_id": str(payment.public_id),
            },
            idempotency_key=payment.idempotency_key,
        )

        payment.gateway = "stripe"
        payment.gateway_payment_id = intent.id
        payment.gateway_response = {
            "client_secret": intent.client_secret,
            "status": intent.status,
        }
        payment.save(
            update_fields=[
                "gateway",
                "gateway_payment_id",
                "gateway_response",
                "updated_at",
            ]
        )
        return payment

    @staticmethod
    def construct_webhook_event(*, payload: bytes, signature: str) -> stripe.Event:
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise BusinessRuleError("Stripe webhook secret is not configured.")
        return stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )

    @staticmethod
    def handle_webhook_event(event: stripe.Event) -> None:
        if StripeWebhookEvent.objects.filter(stripe_event_id=event.id).exists():
            logger.info("Skipping duplicate Stripe webhook event %s", event.id)
            return

        event_type = event.type
        data_object = event.data.object

        if event_type == "payment_intent.succeeded":
            PaymentService._handle_payment_intent_succeeded(
                payment_intent=data_object,
                stripe_event_id=event.id,
                event_type=event_type,
            )
        elif event_type == "payment_intent.payment_failed":
            PaymentService._handle_payment_intent_failed(
                payment_intent=data_object,
                stripe_event_id=event.id,
                event_type=event_type,
            )
        else:
            logger.debug("Ignoring unhandled Stripe event type: %s", event_type)

    @staticmethod
    @transaction.atomic
    def _handle_payment_intent_succeeded(
        *,
        payment_intent: dict[str, Any],
        stripe_event_id: str,
        event_type: str,
    ) -> None:
        payment_intent_id = payment_intent.get("id", "")
        payment = (
            Payment.objects.select_for_update()
            .select_related("order", "order__customer")
            .filter(gateway_payment_id=payment_intent_id)
            .first()
        )
        if not payment:
            raise NotFoundError(f"Payment not found for intent {payment_intent_id}.")

        order = payment.order
        StripeWebhookEvent.objects.create(
            stripe_event_id=stripe_event_id,
            event_type=event_type,
            payment_intent_id=payment_intent_id,
            order_id=order.id,
            payload={"id": payment_intent_id, "status": payment_intent.get("status")},
        )

        if order.payment_status == Order.PaymentStatus.PAID:
            logger.info("Order %s already paid; skipping duplicate webhook.", order.order_number)
            return

        InventoryService.validate_order_availability(order)
        payment.gateway_response = {
            **payment.gateway_response,
            "status": payment_intent.get("status"),
            "webhook_confirmed_at": timezone.now().isoformat(),
        }
        payment.save(update_fields=["gateway_response", "updated_at"])

        OrderService.mark_paid(order, payment=payment)
        send_order_confirmation_email(order)

    @staticmethod
    @transaction.atomic
    def _handle_payment_intent_failed(
        *,
        payment_intent: dict[str, Any],
        stripe_event_id: str,
        event_type: str,
    ) -> None:
        payment_intent_id = payment_intent.get("id", "")
        payment = (
            Payment.objects.select_for_update()
            .select_related("order")
            .filter(gateway_payment_id=payment_intent_id)
            .first()
        )
        if not payment:
            raise NotFoundError(f"Payment not found for intent {payment_intent_id}.")

        StripeWebhookEvent.objects.create(
            stripe_event_id=stripe_event_id,
            event_type=event_type,
            payment_intent_id=payment_intent_id,
            order_id=payment.order_id,
            payload={"id": payment_intent_id, "status": payment_intent.get("status")},
        )

        if payment.order.payment_status == Order.PaymentStatus.PAID:
            return

        OrderService.mark_payment_failed(payment.order, payment=payment)
