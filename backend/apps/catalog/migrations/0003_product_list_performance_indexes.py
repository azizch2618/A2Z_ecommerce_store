from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0002_product_reviews_and_specs"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="product",
            index=models.Index(
                fields=["is_active", "deleted_at", "visibility"],
                name="idx_products_visibility_active",
            ),
        ),
    ]
