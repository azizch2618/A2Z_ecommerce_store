"""Scheduled report delivery."""
from __future__ import annotations

from datetime import timedelta

from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from apps.analytics.constants import ReportFormat, ScheduleFrequency
from apps.analytics.export import export_report
from apps.analytics.models import ScheduledReport
from apps.core.exceptions import BusinessRuleError, NotFoundError
from apps.erp.services.notifications import NotificationService


class ScheduledReportService:
    @staticmethod
    def list_schedules(*, user=None) -> list[ScheduledReport]:
        qs = ScheduledReport.objects.select_related("created_by")
        if user and not getattr(user, "is_superuser", False):
            qs = qs.filter(created_by=user)
        return list(qs.order_by("name"))

    @staticmethod
    def get_schedule(public_id) -> ScheduledReport:
        schedule = ScheduledReport.objects.filter(public_id=public_id).first()
        if not schedule:
            raise NotFoundError("Scheduled report not found.")
        return schedule

    @classmethod
    @transaction.atomic
    def create(
        cls,
        *,
        actor,
        name: str,
        report_id: str,
        export_format: str = ReportFormat.CSV,
        frequency: str = ScheduleFrequency.WEEKLY,
        recipient_emails: list[str] | None = None,
    ) -> ScheduledReport:
        if not recipient_emails:
            raise BusinessRuleError("At least one recipient email is required.")
        now = timezone.now()
        schedule = ScheduledReport.objects.create(
            name=name,
            report_id=report_id,
            export_format=export_format,
            frequency=frequency,
            recipient_emails=recipient_emails,
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
            next_run_at=cls._next_run(from_dt=now, frequency=frequency),
        )
        return schedule

    @classmethod
    def _next_run(cls, *, from_dt, frequency: str):
        if frequency == ScheduleFrequency.DAILY:
            return from_dt + timedelta(days=1)
        if frequency == ScheduleFrequency.MONTHLY:
            return from_dt + timedelta(days=30)
        return from_dt + timedelta(days=7)

    @classmethod
    def deliver(cls, *, schedule: ScheduledReport) -> None:
        actor = schedule.created_by
        if not actor:
            return

        payload = export_report(
            report_id=schedule.report_id,
            export_format=schedule.export_format,
            user=actor,
        )

        subject = f"Scheduled report: {schedule.name}"
        body = f"Your scheduled report '{schedule.name}' is attached ({payload['filename']})."

        for email in schedule.recipient_emails:
            if schedule.export_format == ReportFormat.CSV:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=None,
                    recipient_list=[email],
                    fail_silently=True,
                )
            else:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=None,
                    recipient_list=[email],
                    fail_silently=True,
                )

            if actor:
                NotificationService.send_from_template(
                    recipient=actor,
                    template_code="report_delivered",
                    context={
                        "report_name": schedule.name,
                        "filename": payload["filename"],
                    },
                    resource_type="scheduled_report",
                    resource_id=str(schedule.public_id),
                )

        schedule.last_run_at = timezone.now()
        schedule.next_run_at = cls._next_run(
            from_dt=schedule.last_run_at,
            frequency=schedule.frequency,
        )
        schedule.save(update_fields=["last_run_at", "next_run_at", "updated_at"])

    @classmethod
    def deliver_due_reports(cls) -> int:
        now = timezone.now()
        due = ScheduledReport.objects.filter(is_active=True, next_run_at__lte=now)
        count = 0
        for schedule in due:
            cls.deliver(schedule=schedule)
            count += 1
        return count
