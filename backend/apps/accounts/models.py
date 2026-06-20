"""User identity, authentication, and RBAC."""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.accounts.managers import UserManager
from apps.core.models import PublicIdModel, SoftDeleteModel


class User(AbstractBaseUser, PermissionsMixin, PublicIdModel, SoftDeleteModel):
    email = models.EmailField(unique=True, db_index=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email


class UserProfile(PublicIdModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    avatar_url = models.URLField(max_length=500, blank=True)
    preferences = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "user_profiles"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=False)

    class Meta:
        db_table = "roles"

    def __str__(self) -> str:
        return self.name


class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    module = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "permissions"

    def __str__(self) -> str:
        return self.codename


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="role_permissions")

    class Meta:
        db_table = "role_permissions"
        unique_together = [("role", "permission")]


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")
    organization = models.ForeignKey(
        "customers.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_roles",
    )

    class Meta:
        db_table = "user_roles"
        unique_together = [("user", "role", "organization")]
