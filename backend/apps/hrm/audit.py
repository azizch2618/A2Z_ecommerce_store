"""HRM audit helper."""
from __future__ import annotations

from typing import Any

from apps.erp.constants import AuditModule
from apps.erp.services.audit import AuditService


class HrmAuditService:
    @staticmethod
    def log(
        *,
        user,
        action: str,
        resource_type: str,
        resource_id: str,
        summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        AuditService.log(
            user=user,
            module=AuditModule.HRM,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            summary=summary,
            metadata=metadata or {},
            mirror_operational=False,
        )
