"""Procurement API permissions."""
from apps.accounts.permissions import HasPermission
from apps.accounts.rbac import PermissionCodename


class CanViewProcurement(HasPermission):
    required_permissions = (PermissionCodename.PROCUREMENT_VIEW,)


class CanManageProcurement(HasPermission):
    required_permissions = (PermissionCodename.PROCUREMENT_MANAGE,)


class CanApproveProcurement(HasPermission):
    required_permissions = (PermissionCodename.PROCUREMENT_APPROVE,)


class CanAccessSupplierPortal(HasPermission):
    required_permissions = (PermissionCodename.SUPPLIER_PORTAL,)
