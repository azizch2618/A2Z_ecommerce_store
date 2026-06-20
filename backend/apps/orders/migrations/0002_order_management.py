"""Order management schema updates."""
from django.db import migrations, models


def migrate_order_statuses(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    mapping = {
        "draft": "pending",
        "pending_payment": "pending",
        "confirmed": "paid",
        "processing": "packed",
        "on_hold": "pending",
        "completed": "delivered",
        "cancelled": "cancelled",
    }
    for old_status, new_status in mapping.items():
        Order.objects.filter(status=old_status).update(status=new_status)


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="billing_address",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="order",
            name="delivered_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="guest_email",
            field=models.EmailField(blank=True, db_index=True, max_length=254),
        ),
        migrations.AddField(
            model_name="order",
            name="packed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="paid_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="payment_method",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name="order",
            name="shipped_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_address",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_method",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.RunPython(migrate_order_statuses, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="order",
            name="order_number",
            field=models.CharField(db_index=True, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name="order",
            name="placed_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("paid", "Paid"),
                    ("packed", "Packed"),
                    ("shipped", "Shipped"),
                    ("delivered", "Delivered"),
                    ("cancelled", "Cancelled"),
                ],
                db_index=True,
                default="pending",
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("authorized", "Authorized"),
                    ("paid", "Paid"),
                    ("failed", "Failed"),
                    ("refunded", "Refunded"),
                    ("partially_refunded", "Partially Refunded"),
                ],
                default="pending",
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="shipment",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("packed", "Packed"),
                    ("shipped", "Shipped"),
                    ("delivered", "Delivered"),
                    ("cancelled", "Cancelled"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="shipment",
            name="tracking_number",
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AlterModelOptions(
            name="order",
            options={"ordering": ["-placed_at", "-created_at"]},
        ),
        migrations.AlterModelOptions(
            name="payment",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterModelOptions(
            name="shipment",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["customer", "-placed_at"], name="idx_orders_customer_placed"),
        ),
    ]
