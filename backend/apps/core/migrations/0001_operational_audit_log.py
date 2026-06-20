import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OperationalAuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("public_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                (
                    "module",
                    models.CharField(
                        choices=[
                            ("catalog", "Catalog"),
                            ("inventory", "Inventory"),
                            ("orders", "Orders"),
                            ("trade", "Trade"),
                            ("suppliers", "Suppliers"),
                            ("reports", "Reports"),
                        ],
                        max_length=30,
                    ),
                ),
                ("action", models.CharField(max_length=50)),
                ("resource_type", models.CharField(max_length=50)),
                ("resource_id", models.CharField(max_length=64)),
                ("details", models.JSONField(blank=True, default=dict)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="operational_audit_logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "operational_audit_logs",
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["module", "-created_at"], name="idx_audit_module_created"),
                    models.Index(fields=["resource_type", "resource_id"], name="idx_audit_resource"),
                ],
            },
        ),
    ]
