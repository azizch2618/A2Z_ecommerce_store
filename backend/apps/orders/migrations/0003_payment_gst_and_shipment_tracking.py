"""Add missing payment and shipment fields."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_order_management"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="gst_cents",
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="shipment",
            name="delivered_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="shipment",
            name="tracking_url",
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
