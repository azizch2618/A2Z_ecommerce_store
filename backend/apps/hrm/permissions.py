"""HRM API permissions."""
from apps.accounts.permissions import HasPermission
from apps.accounts.rbac import PermissionCodename


class CanViewHrm(HasPermission):
    required_permissions = (PermissionCodename.HRM_VIEW,)


class CanManageHrm(HasPermission):
    required_permissions = (PermissionCodename.HRM_MANAGE,)


class CanApproveHrm(HasPermission):
    required_permissions = (PermissionCodename.HRM_APPROVE,)


class CanSelfHrm(HasPermission):
    required_permissions = (PermissionCodename.HRM_SELF,)
