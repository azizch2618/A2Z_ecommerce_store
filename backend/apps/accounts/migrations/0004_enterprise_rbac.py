# Enterprise RBAC — roles, permissions, and role-permission matrix

from django.db import migrations

from apps.accounts.constants import SYSTEM_ROLES
from apps.accounts.rbac import ROLE_PERMISSIONS, SYSTEM_PERMISSIONS


def seed_enterprise_rbac(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Permission = apps.get_model("accounts", "Permission")
    RolePermission = apps.get_model("accounts", "RolePermission")
    UserRole = apps.get_model("accounts", "UserRole")

    for role_data in SYSTEM_ROLES:
        Role.objects.update_or_create(
            slug=role_data["slug"],
            defaults={
                "name": role_data["name"],
                "description": role_data["description"],
                "is_system": role_data["is_system"],
            },
        )

    for perm_data in SYSTEM_PERMISSIONS:
        Permission.objects.update_or_create(
            codename=perm_data["codename"],
            defaults={
                "module": perm_data["module"],
                "description": perm_data["description"],
            },
        )

    for role_slug, codenames in ROLE_PERMISSIONS.items():
        role = Role.objects.filter(slug=str(role_slug)).first()
        if not role:
            continue
        for codename in codenames:
            permission = Permission.objects.filter(codename=codename).first()
            if permission:
                RolePermission.objects.get_or_create(role=role, permission=permission)

    # Migrate legacy staff users to manager role
    staff_role = Role.objects.filter(slug="staff").first()
    manager_role = Role.objects.filter(slug="manager").first()
    if staff_role and manager_role:
        staff_user_ids = UserRole.objects.filter(role=staff_role).values_list(
            "user_id", flat=True
        )
        for user_id in staff_user_ids:
            UserRole.objects.get_or_create(
                user_id=user_id,
                role=manager_role,
                organization=None,
            )


def reverse_seed(apps, schema_editor):
    Permission = apps.get_model("accounts", "Permission")
    new_slugs = {
        "super-admin",
        "manager",
        "warehouse-manager",
        "sales-representative",
        "customer-service",
    }
    Role = apps.get_model("accounts", "Role")
    Role.objects.filter(slug__in=new_slugs).delete()
    Permission.objects.filter(
        codename__in=[p["codename"] for p in SYSTEM_PERMISSIONS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_seed_system_roles"),
    ]

    operations = [
        migrations.RunPython(seed_enterprise_rbac, reverse_seed),
    ]
