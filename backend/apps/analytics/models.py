"""Analytics event tracking."""
from django.db import models

from apps.core.models import PublicIdModel


class AnalyticsEvent(PublicIdModel):
    event_type = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="analytics_events",
    )
    session_id = models.CharField(max_length=64, blank=True, db_index=True)
    properties = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(db_index=True)

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
