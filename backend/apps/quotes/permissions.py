"""Quote API permissions."""
from apps.accounts.permissions import HasPermission
from apps.accounts.rbac import PermissionCodename


class CanViewQuotes(HasPermission):
    required_permissions = (PermissionCodename.QUOTES_VIEW,)


class CanManageQuotes(HasPermission):
    required_permissions = (PermissionCodename.QUOTES_MANAGE,)


class CanApproveQuotes(HasPermission):
    required_permissions = (PermissionCodename.QUOTES_APPROVE,)
