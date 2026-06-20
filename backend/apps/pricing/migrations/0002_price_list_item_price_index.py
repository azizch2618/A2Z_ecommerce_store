from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pricing", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="pricelistitem",
            index=models.Index(
                fields=["price_list", "unit_price_ex_gst_cents"],
                name="idx_price_list_items_price",
            ),
        ),
    ]
