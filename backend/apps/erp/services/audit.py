"""Global audit event service."""
from __future__ import annotations

from typing import Any

from apps.core.audit import log_operation
from apps.core.models import OperationalAuditLog
from apps.erp.constants import AuditModule
from apps.erp.models import AuditEvent


class AuditService:
    """Write to global audit log; optionally mirror to operational audit."""

    MODULE_MAP: dict[str, str] = {
        AuditModule.CATALOG: OperationalAuditLog.Module.CATALOG,
        AuditModule.INVENTORY: OperationalAuditLog.Module.INVENTORY,
        AuditModule.ORDERS: OperationalAuditLog.Module.ORDERS,
        AuditModule.TRADE: OperationalAuditLog.Module.TRADE,
        AuditModule.SUPPLIERS: OperationalAuditLog.Module.SUPPLIERS,
        AuditModule.REPORTS: OperationalAuditLog.Module.REPORTS,
    }

    @staticmethod
    def log(
        *,
        user,
        module: str,
        action: str,
        resource_type: str,
        resource_id: str,
        summary: str = "",
        changes: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        ip_address: str | None = None,
        mirror_operational: bool = True,
    ) -> AuditEvent:
        event = AuditEvent.objects.create(
            user=user if getattr(user, "is_authenticated", False) else None,
            module=module,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            summary=summary,
            changes=changes or {},
            metadata=metadata or {},
            ip_address=ip_address,
        )

        if mirror_operational and module in AuditService.MODULE_MAP:
            log_operation(
                user=user,
                module=AuditService.MODULE_MAP[module],
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id),
                details={"summary": summary, **(metadata or {}), **(changes or {})},
            )

        return event
