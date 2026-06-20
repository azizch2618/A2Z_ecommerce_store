"""Shared DRF permission classes."""
from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """Require an authenticated Django staff user."""

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
