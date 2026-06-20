# Generated manually — ERP inventory enhancements

import uuid

from django.db import migrations, models
import django.db.models.deletion


def backfill_movement_numbers(apps, schema_editor):
    InventoryTransaction = apps.get_model("inventory", "InventoryTransaction")
    for tx in InventoryTransaction.objects.all().iterator():
        if not tx.movement_number:
            tx.movement_number = f"LEGACY-{tx.pk}-{uuid.uuid4().hex[:6].upper()}"
            tx.save(update_fields=["movement_number"])


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
        ("suppliers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="inventorylevel",
            name="average_cost_cents",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inventorylevel",
            name="last_cost_cents",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inventorylevel",
            name="last_sale_price_cents",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="inventorytransaction",
            name="movement_number",
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AddField(
            model_name="inventorytransaction",
            name="sale_price_cents",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="inventorytransaction",
            name="transfer_group_id",
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="inventorytransaction",
            name="supplier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="stock_movements",
                to="suppliers.supplier",
            ),
        ),
        migrations.RunPython(backfill_movement_numbers, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="inventorytransaction",
            name="movement_number",
            field=models.CharField(max_length=40, unique=True),
        ),
        migrations.AddIndex(
            model_name="inventorylevel",
            index=models.Index(fields=["variant"], name="idx_inventory_variant"),
        ),
        migrations.AddIndex(
            model_name="inventorylevel",
            index=models.Index(fields=["warehouse"], name="idx_inventory_warehouse"),
        ),
        migrations.AddIndex(
            model_name="inventorytransaction",
            index=models.Index(fields=["variant", "created_at"], name="idx_stock_mv_variant_dt"),
        ),
        migrations.AddIndex(
            model_name="inventorytransaction",
            index=models.Index(fields=["transaction_type", "created_at"], name="idx_stock_mv_type_dt"),
        ),
    ]
