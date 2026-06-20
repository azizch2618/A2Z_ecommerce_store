"""WMS API permissions."""
from apps.accounts.permissions import HasPermission
from apps.accounts.rbac import PermissionCodename


class CanViewWms(HasPermission):
    required_permissions = (PermissionCodename.WMS_VIEW,)


class CanManageWms(HasPermission):
    required_permissions = (PermissionCodename.WMS_MANAGE,)


class CanApproveWms(HasPermission):
    required_permissions = (PermissionCodename.WMS_APPROVE,)


class CanExecuteWms(HasPermission):
    required_permissions = (PermissionCodename.WMS_EXECUTE,)
