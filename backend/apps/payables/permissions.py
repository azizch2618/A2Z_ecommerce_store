"""Payables API permissions."""
from apps.accounts.permissions import HasPermission
from apps.accounts.rbac import PermissionCodename


class CanViewPayables(HasPermission):
    required_permissions = (PermissionCodename.PAYABLES_VIEW,)


class CanManagePayables(HasPermission):
    required_permissions = (PermissionCodename.PAYABLES_MANAGE,)


class CanApprovePayables(HasPermission):
    required_permissions = (PermissionCodename.PAYABLES_APPROVE,)
