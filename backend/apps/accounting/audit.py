"""Accounting audit helper."""
from __future__ import annotations

from typing import Any

from apps.accounting.models import AccountingAuditLog
from apps.erp.constants import AuditModule
from apps.erp.services.audit import AuditService


class AccountingAuditService:
    @staticmethod
    def log(
        *,
        user,
        action: str,
        resource_type: str,
        resource_id: str,
        summary: str,
        metadata: dict[str, Any] | None = None,
    ) -> AccountingAuditLog:
        entry = AccountingAuditLog.objects.create(
            user=user if getattr(user, "is_authenticated", False) else None,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            summary=summary,
            metadata=metadata or {},
        )
        AuditService.log(
            user=user,
            module=AuditModule.ACCOUNTING,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            summary=summary,
            metadata=metadata,
            mirror_operational=False,
        )
        return entry
