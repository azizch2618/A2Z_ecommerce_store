"""Payroll API permissions."""
from apps.accounts.permissions import HasPermission
from apps.accounts.rbac import PermissionCodename


class CanViewPayroll(HasPermission):
    required_permissions = (PermissionCodename.PAYROLL_VIEW,)


class CanManagePayroll(HasPermission):
    required_permissions = (PermissionCodename.PAYROLL_MANAGE,)


class CanApprovePayroll(HasPermission):
    required_permissions = (PermissionCodename.PAYROLL_APPROVE,)


class CanPostPayroll(HasPermission):
    required_permissions = (PermissionCodename.PAYROLL_POST,)
