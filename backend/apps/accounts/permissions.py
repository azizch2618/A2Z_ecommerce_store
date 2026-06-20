"""DRF permission classes for enterprise RBAC."""

from __future__ import annotations

from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.accounts.constants import ADMIN_PORTAL_ROLES, RoleSlug
from apps.accounts.rbac import PermissionCodename
from apps.accounts.services import PermissionService, RoleService


class IsAuthenticatedUser(IsAuthenticated):
    """Authenticated storefront or staff user."""


class IsEmailVerified(BasePermission):
    message = "Email verification is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.email_verified_at is not None
        )


class HasRole(BasePermission):
    """Require at least one of the configured role slugs."""

    required_roles: tuple[RoleSlug | str, ...] = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        roles = getattr(view, "required_roles", None) or self.required_roles
        return RoleService.has_any_role(request.user, tuple(roles))


class HasPermission(BasePermission):
    """Require permission codename(s) from the RBAC matrix."""

    required_permissions: tuple[str, ...] = ()
    require_all_permissions: bool = False

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        perms = getattr(view, "required_permissions", None) or self.required_permissions
        if not perms:
            return False

        require_all = getattr(
            view, "require_all_permissions", self.require_all_permissions
        )
        if require_all:
            return all(
                PermissionService.has_permission(request.user, p) for p in perms
            )
        return PermissionService.has_any_permission(request.user, tuple(perms))


def require_permissions(
    *codenames: str,
    require_all: bool = False,
) -> type[HasPermission]:
    """Factory for view-specific permission classes."""

    class _Permission(HasPermission):
        required_permissions = codenames
        require_all_permissions = require_all

    return _Permission


# ---------------------------------------------------------------------------
# Role-based shortcuts
# ---------------------------------------------------------------------------

class IsSuperAdmin(HasRole):
    required_roles = (RoleSlug.SUPER_ADMIN,)


class IsAdmin(HasRole):
    required_roles = (RoleSlug.SUPER_ADMIN, RoleSlug.ADMIN)


class IsInternalStaff(HasRole):
    """Any role that can access the admin portal."""

    required_roles = tuple(ADMIN_PORTAL_ROLES)


class IsCustomer(HasRole):
    required_roles = (RoleSlug.CUSTOMER,)


class IsTradeCustomer(HasRole):
    required_roles = (RoleSlug.TRADE_CUSTOMER,)


# Legacy alias
class IsStaff(HasRole):
    required_roles = tuple(ADMIN_PORTAL_ROLES)


# ---------------------------------------------------------------------------
# Module permission shortcuts
# ---------------------------------------------------------------------------

class CanViewDashboard(HasPermission):
    required_permissions = (PermissionCodename.DASHBOARD_VIEW,)


class CanViewCatalog(HasPermission):
    required_permissions = (PermissionCodename.CATALOG_VIEW,)


class CanManageCatalog(HasPermission):
    required_permissions = (PermissionCodename.CATALOG_MANAGE,)


class CanViewInventory(HasPermission):
    required_permissions = (PermissionCodename.INVENTORY_VIEW,)


class CanManageInventory(HasPermission):
    required_permissions = (PermissionCodename.INVENTORY_MANAGE,)


class CanViewOrders(HasPermission):
    required_permissions = (PermissionCodename.ORDERS_VIEW,)


class CanManageOrders(HasPermission):
    required_permissions = (PermissionCodename.ORDERS_MANAGE,)


class CanViewCustomers(HasPermission):
    required_permissions = (PermissionCodename.CUSTOMERS_VIEW,)


class CanManageCustomers(HasPermission):
    required_permissions = (PermissionCodename.CUSTOMERS_MANAGE,)


class CanViewSuppliers(HasPermission):
    required_permissions = (PermissionCodename.SUPPLIERS_VIEW,)


class CanManageSuppliers(HasPermission):
    required_permissions = (PermissionCodename.SUPPLIERS_MANAGE,)


class CanViewTrade(HasPermission):
    required_permissions = (PermissionCodename.TRADE_VIEW,)


class CanApproveTrade(HasPermission):
    required_permissions = (PermissionCodename.TRADE_APPROVE,)


class CanManageWarehouse(HasPermission):
    required_permissions = (PermissionCodename.WAREHOUSE_MANAGE,)


class CanViewReports(HasPermission):
    required_permissions = (PermissionCodename.REPORTS_VIEW,)


class CanExportReports(HasPermission):
    required_permissions = (PermissionCodename.REPORTS_EXPORT,)


class CanCheckout(HasPermission):
    required_permissions = (PermissionCodename.STORE_CHECKOUT,)
