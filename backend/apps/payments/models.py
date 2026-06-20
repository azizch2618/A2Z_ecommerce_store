"""Stripe webhook idempotency and audit records."""
from django.db import models

from apps.core.models import PublicIdModel


class StripeWebhookEvent(PublicIdModel):
    """Processed Stripe webhook events — prevents duplicate handling."""

    stripe_event_id = models.CharField(max_length=255, unique=True, db_index=True)
    event_type = models.CharField(max_length=100, db_index=True)
    payment_intent_id = models.CharField(max_length=100, blank=True, db_index=True)
    order_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "stripe_webhook_events"
        ordering = ["-processed_at"]

    def __str__(self) -> str:
        return f"{self.event_type}:{self.stripe_event_id}"
