"""Celery tasks for scheduled BI report delivery."""
from celery import shared_task


@shared_task(name="analytics.deliver_scheduled_reports")
def deliver_scheduled_reports() -> int:
    from apps.analytics.scheduled_reports import ScheduledReportService

    return ScheduledReportService.deliver_due_reports()
