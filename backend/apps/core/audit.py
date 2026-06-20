"""Operational audit logging helper."""
from __future__ import annotations

from typing import Any

from apps.core.models import OperationalAuditLog


def log_operation(
    *,
    user,
    module: str,
    action: str,
    resource_type: str,
    resource_id: str,
    details: dict[str, Any] | None = None,
) -> OperationalAuditLog:
    return OperationalAuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        module=module,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        details=details or {},
    )
