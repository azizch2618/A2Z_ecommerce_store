"""Accounting API permissions."""
from apps.accounts.permissions import HasPermission
from apps.accounts.rbac import PermissionCodename


class CanViewAccounting(HasPermission):
    required_permissions = (PermissionCodename.ACCOUNTING_VIEW,)


class CanManageAccounting(HasPermission):
    required_permissions = (PermissionCodename.ACCOUNTING_MANAGE,)


class CanPostAccounting(HasPermission):
    required_permissions = (PermissionCodename.ACCOUNTING_POST,)
