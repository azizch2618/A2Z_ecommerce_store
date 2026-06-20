"""Notification delivery service."""
from __future__ import annotations

from typing import Any

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from apps.erp.constants import NotificationChannel, NotificationStatus
from apps.erp.models import Notification, NotificationTemplate


class NotificationService:
    @staticmethod
    def render_template(template: NotificationTemplate, context: dict[str, Any]) -> tuple[str, str]:
        subject = template.subject_template
        body = template.body_template
        for key, value in context.items():
            token = "{" + key + "}"
            subject = subject.replace(token, str(value))
            body = body.replace(token, str(value))
        return subject, body

    @classmethod
    def send(
        cls,
        *,
        recipient,
        channel: str,
        subject: str,
        body: str,
        template: NotificationTemplate | None = None,
        resource_type: str = "",
        resource_id: str = "",
        metadata: dict[str, Any] | None = None,
        deliver_now: bool = True,
    ) -> Notification:
        notification = Notification.objects.create(
            recipient=recipient,
            channel=channel,
            template=template,
            subject=subject,
            body=body,
            status=NotificationStatus.PENDING,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else "",
            metadata=metadata or {},
        )

        if deliver_now:
            cls.deliver(notification)

        return notification

    @classmethod
    def send_from_template(
        cls,
        *,
        recipient,
        template_code: str,
        context: dict[str, Any],
        resource_type: str = "",
        resource_id: str = "",
        deliver_now: bool = True,
    ) -> Notification | None:
        template = NotificationTemplate.objects.filter(
            code=template_code,
            is_active=True,
        ).first()
        if template is None:
            return None
        subject, body = cls.render_template(template, context)
        return cls.send(
            recipient=recipient,
            channel=template.channel,
            subject=subject,
            body=body,
            template=template,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata={"template_code": template_code, "context": context},
            deliver_now=deliver_now,
        )

    @staticmethod
    def deliver(notification: Notification) -> None:
        if notification.channel == NotificationChannel.EMAIL:
            send_mail(
                subject=notification.subject,
                message=notification.body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@a2ztools.com.au"),
                recipient_list=[notification.recipient.email],
                fail_silently=False,
            )
            notification.status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
        elif notification.channel == NotificationChannel.IN_APP:
            notification.status = NotificationStatus.SENT
            notification.sent_at = timezone.now()
        elif notification.channel == NotificationChannel.SMS:
            notification.status = NotificationStatus.PENDING
            notification.metadata = {
                **notification.metadata,
                "sms_deferred": True,
                "note": "SMS channel reserved for future integration",
            }
        notification.save(
            update_fields=["status", "sent_at", "metadata", "updated_at"],
        )

    @staticmethod
    def mark_read(notification: Notification) -> None:
        notification.status = NotificationStatus.READ
        notification.read_at = timezone.now()
        notification.save(update_fields=["status", "read_at", "updated_at"])
