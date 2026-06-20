"""CRM models — linked to ERP Party, not duplicate customer master data."""
from __future__ import annotations

from django.db import models

from apps.core.models import PublicIdModel, SoftDeleteModel
from apps.crm.constants import ActivityType, LeadSource, LeadStatus, OpportunityStatus


class CrmLead(PublicIdModel, SoftDeleteModel):
    """Sales lead — resolves to Party on creation or qualification."""

    party = models.ForeignKey(
        "erp.Party",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_leads",
    )
    title = models.CharField(max_length=255, help_text="Lead name / primary contact label")
    company_name = models.CharField(max_length=255, blank=True)
    contact_name = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    source = models.CharField(
        max_length=30,
        choices=LeadSource.choices,
        default=LeadSource.WEBSITE,
    )
    status = models.CharField(
        max_length=20,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW,
        db_index=True,
    )
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_crm_leads",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_leads",
        help_text="Set when lead converts to customer",
    )
    notes_summary = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "crm_leads"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"], name="idx_crm_lead_status"),
            models.Index(fields=["assigned_to", "status"], name="idx_crm_lead_assignee"),
        ]

    def __str__(self) -> str:
        return self.title


class CrmOpportunity(PublicIdModel, SoftDeleteModel):
    """Sales opportunity — links Party, optional Lead, Customer, TradeAccount."""

    party = models.ForeignKey(
        "erp.Party",
        on_delete=models.PROTECT,
        related_name="crm_opportunities",
    )
    lead = models.ForeignKey(
        CrmLead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_opportunities",
    )
    trade_account = models.ForeignKey(
        "trade_accounts.TradeAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_opportunities",
    )
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10,
        choices=OpportunityStatus.choices,
        default=OpportunityStatus.OPEN,
        db_index=True,
    )
    stage = models.CharField(
        max_length=30,
        choices=LeadStatus.choices,
        default=LeadStatus.QUALIFIED,
        help_text="Pipeline stage aligned with lead statuses",
    )
    expected_revenue_cents = models.BigIntegerField(default=0)
    probability = models.PositiveSmallIntegerField(default=0)
    expected_close_date = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_crm_opportunities",
    )
    won_at = models.DateTimeField(null=True, blank=True)
    lost_at = models.DateTimeField(null=True, blank=True)
    lost_reason = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "crm_opportunities"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"], name="idx_crm_opp_status"),
            models.Index(fields=["assigned_to", "status"], name="idx_crm_opp_assignee"),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def weighted_revenue_cents(self) -> int:
        return int(self.expected_revenue_cents * self.probability / 100)


class CrmActivity(PublicIdModel):
    """Scheduled or completed sales activity."""

    party = models.ForeignKey(
        "erp.Party",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="crm_activities",
    )
    lead = models.ForeignKey(
        CrmLead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="activities",
    )
    opportunity = models.ForeignKey(
        CrmOpportunity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="activities",
    )
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_activities",
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_activities_created",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "crm_activities"
        ordering = ["-created_at"]
        verbose_name_plural = "CRM activities"


class CrmNote(PublicIdModel):
    """Free-form note on lead, opportunity, or party."""

    party = models.ForeignKey(
        "erp.Party",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="crm_notes",
    )
    lead = models.ForeignKey(
        CrmLead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notes",
    )
    opportunity = models.ForeignKey(
        CrmOpportunity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notes",
    )
    body = models.TextField()
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crm_notes_created",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "crm_notes"
        ordering = ["-created_at"]
