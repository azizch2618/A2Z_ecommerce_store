"""Receivables API permissions."""
from apps.accounts.permissions import HasPermission
from apps.accounts.rbac import PermissionCodename


class CanViewReceivables(HasPermission):
    required_permissions = (PermissionCodename.RECEIVABLES_VIEW,)


class CanManageReceivables(HasPermission):
    required_permissions = (PermissionCodename.RECEIVABLES_MANAGE,)


class CanApproveReceivables(HasPermission):
    required_permissions = (PermissionCodename.RECEIVABLES_APPROVE,)
