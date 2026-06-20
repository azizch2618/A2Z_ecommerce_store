"""ERP foundation data models."""
from __future__ import annotations

import uuid

from django.db import models

from apps.core.models import PublicIdModel, SoftDeleteModel, TimeStampedModel
from apps.core.validators import validate_australian_postcode, validate_australian_state
from apps.erp.constants import (
    AddressType,
    AuditModule,
    DomainEventStatus,
    NotificationChannel,
    NotificationStatus,
    PartyRole,
    PartyType,
    WorkflowInstanceStatus,
)


# ---------------------------------------------------------------------------
# 1. Company hierarchy
# ---------------------------------------------------------------------------


class Company(PublicIdModel, SoftDeleteModel):
    """Legal entity — root of the org structure."""

    code = models.CharField(max_length=20, unique=True)
    legal_name = models.CharField(max_length=255)
    trading_name = models.CharField(max_length=255, blank=True)
    abn = models.CharField(max_length=11, blank=True)
    acn = models.CharField(max_length=9, blank=True)
    gst_registered = models.BooleanField(default=True)
    base_currency = models.CharField(max_length=3, default="AUD")
    fiscal_year_start_month = models.PositiveSmallIntegerField(default=7)  # AU: July
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_companies"
        verbose_name_plural = "companies"

    def __str__(self) -> str:
        return self.trading_name or self.legal_name


class BusinessUnit(PublicIdModel, SoftDeleteModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="business_units")
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_business_units"
        unique_together = [("company", "code")]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class Department(PublicIdModel, SoftDeleteModel):
    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        related_name="departments",
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_departments"
        unique_together = [("business_unit", "code")]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class CostCenter(PublicIdModel, SoftDeleteModel):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="cost_centers",
    )
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_cost_centers"
        unique_together = [("department", "code")]
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


# ---------------------------------------------------------------------------
# 2. Party model
# ---------------------------------------------------------------------------


class Party(PublicIdModel, SoftDeleteModel):
    """Unified master record for customers, suppliers, employees, and contacts."""

    party_type = models.CharField(max_length=20, choices=PartyType.choices)
    display_name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True)
    tax_id = models.CharField(max_length=20, blank=True, help_text="ABN or tax identifier")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="parties",
    )
    customer = models.OneToOneField(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="party",
    )
    supplier = models.OneToOneField(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="party",
    )
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="party",
        help_text="Future HRM employee link",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_parties"
        verbose_name_plural = "parties"
        indexes = [
            models.Index(fields=["party_type", "is_active"], name="idx_party_type_active"),
            models.Index(fields=["display_name"], name="idx_party_display_name"),
        ]

    def __str__(self) -> str:
        return self.display_name

    @property
    def roles(self) -> list[str]:
        roles: list[str] = []
        if self.customer_id:
            roles.append(PartyRole.CUSTOMER)
        if self.supplier_id:
            roles.append(PartyRole.SUPPLIER)
        if self.user_id:
            roles.append(PartyRole.EMPLOYEE)
        if not roles:
            roles.append(PartyRole.CONTACT)
        return roles


# ---------------------------------------------------------------------------
# 3. Contact model
# ---------------------------------------------------------------------------


class Contact(PublicIdModel, SoftDeleteModel):
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name="contacts")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_contacts"
        ordering = ["-is_primary", "last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


# ---------------------------------------------------------------------------
# 4. Address model (reusable)
# ---------------------------------------------------------------------------


class CoreAddress(PublicIdModel, SoftDeleteModel):
    """Normalized address attachable to parties, warehouses, or legacy entities."""

    class OwnerKind(models.TextChoices):
        PARTY = "party", "Party"
        WAREHOUSE = "warehouse", "Warehouse"
        CUSTOMER = "customer", "Customer"

    owner_kind = models.CharField(max_length=20, choices=OwnerKind.choices)
    party = models.ForeignKey(
        Party,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="addresses",
    )
    warehouse = models.ForeignKey(
        "inventory.Warehouse",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="core_addresses",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="core_addresses",
    )
    address_type = models.CharField(
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.SHIPPING,
    )
    label = models.CharField(max_length=50, blank=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    suburb = models.CharField(max_length=100)
    state = models.CharField(max_length=3, validators=[validate_australian_state])
    postcode = models.CharField(max_length=4, validators=[validate_australian_postcode])
    country = models.CharField(max_length=2, default="AU")
    is_default = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_addresses"
        verbose_name_plural = "core addresses"
        indexes = [
            models.Index(fields=["owner_kind", "address_type"], name="idx_core_addr_owner_type"),
        ]

    def __str__(self) -> str:
        return f"{self.line1}, {self.suburb} {self.state}"


# ---------------------------------------------------------------------------
# 5. Document numbering
# ---------------------------------------------------------------------------


class DocumentSequence(PublicIdModel):
    """Atomic configurable document number sequences."""

    class ResetPeriod(models.TextChoices):
        NEVER = "never", "Never"
        YEARLY = "yearly", "Yearly"
        MONTHLY = "monthly", "Monthly"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="document_sequences",
    )
    code = models.CharField(max_length=10, help_text="Document type code, e.g. SO, PO, INV")
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=10, help_text="Prefix before year segment, e.g. SO-")
    pattern = models.CharField(
        max_length=100,
        default="{prefix}{year}-{seq}",
        help_text="Tokens: {prefix}, {year}, {month}, {seq}",
    )
    reset_period = models.CharField(
        max_length=10,
        choices=ResetPeriod.choices,
        default=ResetPeriod.YEARLY,
    )
    padding = models.PositiveSmallIntegerField(default=6)
    next_value = models.PositiveIntegerField(default=1)
    last_reset_key = models.CharField(max_length=10, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "core_document_sequences"
        unique_together = [("company", "code")]
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} ({self.prefix})"


# ---------------------------------------------------------------------------
# 6. Global audit framework
# ---------------------------------------------------------------------------


class AuditEvent(PublicIdModel):
    """Append-only global audit log for all modules."""

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    module = models.CharField(max_length=30, choices=AuditModule.choices)
    action = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=64)
    summary = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "core_audit_events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["module", "-created_at"], name="idx_audit_evt_module"),
            models.Index(fields=["resource_type", "resource_id"], name="idx_audit_evt_resource"),
            models.Index(fields=["user", "-created_at"], name="idx_audit_evt_user"),
        ]

    def __str__(self) -> str:
        return f"{self.module}.{self.action} on {self.resource_type}:{self.resource_id}"


# ---------------------------------------------------------------------------
# 7. Notification engine
# ---------------------------------------------------------------------------


class NotificationTemplate(PublicIdModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    subject_template = models.CharField(max_length=255, blank=True)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_notification_templates"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code


class Notification(PublicIdModel):
    recipient = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    channel = models.CharField(max_length=10, choices=NotificationChannel.choices)
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )
    resource_type = models.CharField(max_length=50, blank=True)
    resource_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "core_notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "status", "-created_at"], name="idx_notif_recipient"),
        ]

    def __str__(self) -> str:
        return f"{self.channel}:{self.subject[:40]}"


# ---------------------------------------------------------------------------
# 8. Workflow engine
# ---------------------------------------------------------------------------


class WorkflowDefinition(PublicIdModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    document_type = models.CharField(max_length=30, blank=True)
    version = models.PositiveIntegerField(default=1)
    initial_state = models.CharField(max_length=50)
    states = models.JSONField(default=list, help_text="List of valid state names")
    transitions = models.JSONField(
        default=list,
        help_text='[{"from","to","action","required_roles":[],"label"}]',
    )
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_workflow_definitions"
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} v{self.version}"


class WorkflowInstance(PublicIdModel):
    definition = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.PROTECT,
        related_name="instances",
    )
    current_state = models.CharField(max_length=50)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=64)
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_workflows",
    )
    status = models.CharField(
        max_length=20,
        choices=WorkflowInstanceStatus.choices,
        default=WorkflowInstanceStatus.ACTIVE,
    )
    history = models.JSONField(default=list)
    completed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_workflow_instances"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["resource_type", "resource_id"],
                name="idx_workflow_resource",
            ),
            models.Index(fields=["status", "-created_at"], name="idx_workflow_status"),
        ]

    def __str__(self) -> str:
        return f"{self.definition.code}:{self.current_state}"


class WorkflowAction(PublicIdModel):
    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name="actions",
    )
    action = models.CharField(max_length=50)
    actor = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_actions",
    )
    from_state = models.CharField(max_length=50)
    to_state = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "core_workflow_actions"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.action}: {self.from_state} → {self.to_state}"


# ---------------------------------------------------------------------------
# 9. Domain events (outbox)
# ---------------------------------------------------------------------------


class DomainEvent(PublicIdModel):
    event_type = models.CharField(max_length=50, db_index=True)
    aggregate_type = models.CharField(max_length=50)
    aggregate_id = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    idempotency_key = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=DomainEventStatus.choices,
        default=DomainEventStatus.PENDING,
    )
    occurred_at = models.DateTimeField(db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = "core_domain_events"
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["status", "occurred_at"], name="idx_domain_evt_pending"),
            models.Index(fields=["aggregate_type", "aggregate_id"], name="idx_domain_evt_agg"),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} [{self.status}]"


class PlatformSetting(PublicIdModel):
    """Key-value platform configuration (replaces env-only company settings)."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="settings",
    )
    key = models.CharField(max_length=100)
    value = models.JSONField(default=dict)
    description = models.CharField(max_length=255, blank=True)
    is_sensitive = models.BooleanField(default=False)

    class Meta:
        db_table = "core_settings"
        unique_together = [("company", "key")]
        ordering = ["key"]

    def __str__(self) -> str:
        return self.key
