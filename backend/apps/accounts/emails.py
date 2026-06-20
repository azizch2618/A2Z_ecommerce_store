"""Transactional authentication emails."""

from django.conf import settings
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.accounts.models import User
from apps.accounts.tokens import email_verification_token, password_reset_token


def _frontend_url(path: str) -> str:
    base = settings.FRONTEND_URL.rstrip("/")
    return f"{base}{path}"


def _user_display_name(user: User) -> str:
    profile = getattr(user, "profile", None)
    if profile and profile.first_name:
        return profile.first_name
    return user.email.split("@")[0]


def send_verification_email(user: User) -> None:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)
    verify_url = _frontend_url(f"/verify-email?uid={uid}&token={token}")

    subject = "Verify your A2Z Tools account"
    message = (
        f"Hi {_user_display_name(user)},\n\n"
        "Please verify your email address by opening the link below:\n\n"
        f"{verify_url}\n\n"
        "If you did not create an account, you can ignore this email.\n\n"
        "— A2Z Tools"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_password_reset_email(user: User) -> None:
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = password_reset_token.make_token(user)
    reset_url = _frontend_url(f"/reset-password?uid={uid}&token={token}")

    subject = "Reset your A2Z Tools password"
    message = (
        f"Hi {_user_display_name(user)},\n\n"
        "We received a request to reset your password. "
        "Open the link below to choose a new password:\n\n"
        f"{reset_url}\n\n"
        "If you did not request a reset, you can ignore this email. "
        "Your password will not change.\n\n"
        "— A2Z Tools"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_password_changed_email(user: User) -> None:
    subject = "Your A2Z Tools password was changed"
    message = (
        f"Hi {_user_display_name(user)},\n\n"
        "Your password was changed successfully. "
        "If you did not make this change, contact support immediately.\n\n"
        "— A2Z Tools"
    )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


__all__ = [
    "send_password_changed_email",
    "send_password_reset_email",
    "send_verification_email",
]
