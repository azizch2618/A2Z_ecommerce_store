# Inventory alerts table

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_enterprise_rbac"),
        ("inventory", "0002_erp_inventory_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="InventoryAlert",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("alert_type", models.CharField(choices=[("low_stock", "Low Stock"), ("out_of_stock", "Out of Stock")], max_length=20)),
                ("status", models.CharField(choices=[("active", "Active"), ("acknowledged", "Acknowledged"), ("resolved", "Resolved")], default="active", max_length=20)),
                ("quantity_on_hand", models.IntegerField()),
                ("reorder_point", models.IntegerField()),
                ("shortfall", models.IntegerField(default=0)),
                ("message", models.TextField(blank=True)),
                ("acknowledged_at", models.DateTimeField(blank=True, null=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("acknowledged_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="acknowledged_inventory_alerts", to=settings.AUTH_USER_MODEL)),
                ("inventory_level", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alerts", to="inventory.inventorylevel")),
            ],
            options={
                "db_table": "inventory_alerts",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="inventoryalert",
            index=models.Index(fields=["status", "created_at"], name="idx_inv_alert_status_dt"),
        ),
        migrations.AddIndex(
            model_name="inventoryalert",
            index=models.Index(fields=["inventory_level", "status"], name="idx_inv_alert_level_st"),
        ),
    ]
