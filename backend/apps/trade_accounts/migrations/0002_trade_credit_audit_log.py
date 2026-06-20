# Generated manually for trade credit audit logging

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_enterprise_rbac"),
        ("orders", "0003_payment_gst_and_shipment_tracking"),
        ("trade_accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TradeCreditAuditLog",
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
                    "action",
                    models.CharField(
                        choices=[
                            ("authorize", "Authorize"),
                            ("charge", "Charge"),
                            ("release", "Release"),
                        ],
                        max_length=20,
                    ),
                ),
                ("amount_cents", models.BigIntegerField()),
                ("credit_limit_cents", models.BigIntegerField()),
                ("credit_used_before", models.BigIntegerField()),
                ("credit_used_after", models.BigIntegerField()),
                ("metadata", models.JSONField(blank=True, default=dict)),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="trade_credit_audit_logs",
                        to="orders.order",
                    ),
                ),
                (
                    "trade_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name="credit_audit_logs",
                        to="trade_accounts.tradeaccount",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="trade_credit_audit_logs",
                        to="accounts.user",
                    ),
                ),
            ],
            options={
                "db_table": "trade_credit_audit_logs",
                "ordering": ["-created_at"],
            },
        ),
    ]
