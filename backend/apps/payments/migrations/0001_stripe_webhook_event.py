# Generated manually for Stripe payment integration

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_payment_gst_and_shipment_tracking"),
    ]

    operations = [
        migrations.CreateModel(
            name="StripeWebhookEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "public_id",
                    models.UUIDField(
                        db_index=True,
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                    ),
                ),
                (
                    "stripe_event_id",
                    models.CharField(db_index=True, max_length=255, unique=True),
                ),
                ("event_type", models.CharField(db_index=True, max_length=100)),
                (
                    "payment_intent_id",
                    models.CharField(blank=True, db_index=True, max_length=100),
                ),
                (
                    "order_id",
                    models.BigIntegerField(blank=True, db_index=True, null=True),
                ),
                ("processed_at", models.DateTimeField(auto_now_add=True)),
                ("payload", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "db_table": "stripe_webhook_events",
                "ordering": ["-processed_at"],
            },
        ),
    ]
