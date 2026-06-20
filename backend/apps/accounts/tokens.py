"""Signed token generators for email verification and password reset."""

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Time-limited token invalidated once email is verified."""

    def _make_hash_value(self, user, timestamp):
        verified = user.email_verified_at.isoformat() if user.email_verified_at else ""
        return f"{user.pk}{user.email}{timestamp}{verified}"


class PasswordResetTokenGenerator(PasswordResetTokenGenerator):
    """Password reset token invalidated on password change."""

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.password}{timestamp}{user.email}"


email_verification_token = EmailVerificationTokenGenerator()
password_reset_token = PasswordResetTokenGenerator()
