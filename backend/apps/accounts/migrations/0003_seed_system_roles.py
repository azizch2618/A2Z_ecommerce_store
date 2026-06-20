# Generated manually — seed system RBAC roles

from django.db import migrations

from apps.accounts.constants import SYSTEM_ROLES


def seed_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    for role_data in SYSTEM_ROLES:
        Role.objects.update_or_create(
            slug=role_data["slug"],
            defaults={
                "name": role_data["name"],
                "description": role_data["description"],
                "is_system": role_data["is_system"],
            },
        )


def unseed_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Role.objects.filter(
        slug__in=[role["slug"] for role in SYSTEM_ROLES],
        is_system=True,
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]
