from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0003_inventory_alerts"),
    ]

    operations = [
        migrations.AddField(
            model_name="warehouse",
            name="capacity_units",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
