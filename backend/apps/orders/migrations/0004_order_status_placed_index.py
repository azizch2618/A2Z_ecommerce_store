from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0003_payment_gst_and_shipment_tracking"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["status", "placed_at"],
                name="idx_orders_status_placed",
            ),
        ),
    ]
