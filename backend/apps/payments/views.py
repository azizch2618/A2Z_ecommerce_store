"""Stripe webhook and public payment configuration endpoints."""
import logging

import stripe
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import BusinessRuleError
from apps.payments.services import PaymentService

logger = logging.getLogger(__name__)


class PaymentConfigView(APIView):
    """GET /payments/config/ — publishable key for Stripe Elements."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
                "stripe_enabled": PaymentService.is_stripe_configured(),
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    """POST /payments/webhook/ — Stripe event handler (signature verified)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        if not signature:
            return Response(
                {"detail": "Missing Stripe signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            event = PaymentService.construct_webhook_event(
                payload=payload,
                signature=signature,
            )
        except ValueError as exc:
            logger.warning("Invalid Stripe webhook payload: %s", exc)
            return Response(
                {"detail": "Invalid payload."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except stripe.error.SignatureVerificationError as exc:
            logger.warning("Stripe signature verification failed: %s", exc)
            return Response(
                {"detail": "Invalid signature."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except BusinessRuleError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            PaymentService.handle_webhook_event(event)
        except Exception:
            logger.exception("Stripe webhook processing failed for event %s", event.id)
            return Response(
                {"detail": "Webhook processing failed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"received": True})
