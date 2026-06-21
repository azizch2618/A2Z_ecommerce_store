"""Analytics BI permissions."""
from apps.accounts.permissions import HasPermission
from apps.accounts.rbac import PermissionCodename


class CanViewAnalytics(HasPermission):
    required_permissions = (PermissionCodename.ANALYTICS_VIEW,)


class CanManageAnalytics(HasPermission):
    required_permissions = (PermissionCodename.ANALYTICS_MANAGE,)


class CanViewReports(HasPermission):
    required_permissions = (PermissionCodename.REPORTS_VIEW,)


class CanExportReports(HasPermission):
    required_permissions = (PermissionCodename.REPORTS_EXPORT,)
