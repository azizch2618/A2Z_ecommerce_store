"""Django admin for accounts."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import Permission, Role, RolePermission, User, UserProfile, UserRole
from apps.accounts.services import RoleService


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 0


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "is_staff", "is_active", "email_verified_at", "created_at")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "profile__first_name", "profile__last_name")
    inlines = (UserProfileInline, UserRoleInline)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Verification", {"fields": ("email_verified_at", "last_login_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at", "deleted_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at", "last_login_at")
    filter_horizontal = ("groups", "user_permissions")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.is_superuser:
            RoleService.ensure_system_roles()
            RoleService.sync_superuser_role(obj)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_system")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Permission)
admin.site.register(RolePermission)
