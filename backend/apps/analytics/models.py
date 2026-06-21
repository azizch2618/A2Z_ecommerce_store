"""Analytics models — event tracking, search logs, KPI definitions, scheduled reports."""
from django.db import models

from apps.analytics.constants import KpiCategory, KpiUnit, ReportFormat, ScheduleFrequency
from apps.core.models import PublicIdModel


class AnalyticsEvent(PublicIdModel):
    event_type = models.CharField(max_length=100, db_index=True)
    session_id = models.CharField(max_length=64, blank=True, db_index=True)
    properties = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(db_index=True)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
    )

    class Meta:
        db_table = "analytics_events"
        ordering = ["-occurred_at"]


class SearchLog(PublicIdModel):
    query = models.CharField(max_length=255)
    results_count = models.PositiveIntegerField(default=0)
    clicked_type = models.CharField(max_length=50, blank=True)
    clicked_id = models.UUIDField(null=True, blank=True)
    session_id = models.CharField(max_length=64, blank=True)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_logs",
    )

    class Meta:
        db_table = "search_logs"


class KpiDefinition(PublicIdModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=KpiCategory.choices, db_index=True)
    metric_key = models.CharField(max_length=80, db_index=True)
    unit = models.CharField(max_length=20, choices=KpiUnit.choices, default=KpiUnit.COUNT)
    target_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "analytics_kpi_definitions"
        ordering = ["category", "display_order", "name"]


class ScheduledReport(PublicIdModel):
    name = models.CharField(max_length=100)
    report_id = models.CharField(max_length=50)
    export_format = models.CharField(
        max_length=10,
        choices=ReportFormat.choices,
        default=ReportFormat.CSV,
    )
    frequency = models.CharField(
        max_length=10,
        choices=ScheduleFrequency.choices,
        default=ScheduleFrequency.WEEKLY,
    )
    recipient_emails = models.JSONField(default=list)
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scheduled_reports",
    )
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    next_run_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "analytics_scheduled_reports"
        ordering = ["name"]
