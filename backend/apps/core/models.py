"""Shared abstract models for all A2Z Tools domain apps."""
import uuid

from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PublicIdModel(TimeStampedModel):
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class OperationalAuditLog(PublicIdModel):
    """Immutable audit trail for admin operational actions."""

    class Module(models.TextChoices):
        CATALOG = "catalog", "Catalog"
        INVENTORY = "inventory", "Inventory"
        ORDERS = "orders", "Orders"
        TRADE = "trade", "Trade"
        SUPPLIERS = "suppliers", "Suppliers"
        REPORTS = "reports", "Reports"

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operational_audit_logs",
    )
    module = models.CharField(max_length=30, choices=Module.choices)
    action = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=64)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "operational_audit_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["module", "-created_at"], name="idx_audit_module_created"),
            models.Index(fields=["resource_type", "resource_id"], name="idx_audit_resource"),
        ]
