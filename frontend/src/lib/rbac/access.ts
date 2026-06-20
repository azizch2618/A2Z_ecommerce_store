import type { PermissionCodename } from "./permissions";
import { Permission } from "./permissions";

/** Route → required permission for admin portal pages. */
export const ADMIN_ROUTE_PERMISSIONS: Record<string, PermissionCodename> = {
  "/admin-dashboard": Permission.DASHBOARD_VIEW,
  "/admin-dashboard/products": Permission.CATALOG_VIEW,
  "/admin-dashboard/categories": Permission.CATALOG_VIEW,
  "/admin-dashboard/brands": Permission.CATALOG_VIEW,
  "/admin-dashboard/inventory": Permission.INVENTORY_VIEW,
  "/admin-dashboard/warehouses": Permission.WAREHOUSE_VIEW,
  "/admin-dashboard/orders": Permission.ORDERS_VIEW,
  "/admin-dashboard/customers": Permission.CUSTOMERS_VIEW,
  "/admin-dashboard/trade-accounts": Permission.TRADE_VIEW,
  "/admin-dashboard/suppliers": Permission.SUPPLIERS_VIEW,
  "/admin-dashboard/reports": Permission.REPORTS_VIEW,
  "/admin-dashboard/analytics": Permission.ANALYTICS_VIEW,
  "/admin-dashboard/settings": Permission.SETTINGS_VIEW,
};

/** Minimum permission to access any admin route. */
export const ADMIN_PORTAL_PERMISSION = Permission.DASHBOARD_VIEW;

/** Storefront routes requiring authentication. */
export const ACCOUNT_ROUTES = ["/account", "/checkout"] as const;

export function getRequiredPermissionForPath(pathname: string): PermissionCodename | null {
  const exact = ADMIN_ROUTE_PERMISSIONS[pathname];
  if (exact) return exact;

  const match = Object.entries(ADMIN_ROUTE_PERMISSIONS).find(([route]) =>
    route !== "/admin-dashboard" && pathname.startsWith(route)
  );
  return match ? match[1] : null;
}

export function hasPermission(
  userPermissions: string[] | undefined,
  codename: PermissionCodename | string
): boolean {
  return (userPermissions ?? []).includes(codename);
}

export function hasAnyPermission(
  userPermissions: string[] | undefined,
  codenames: (PermissionCodename | string)[]
): boolean {
  const set = new Set(userPermissions ?? []);
  return codenames.some((c) => set.has(c));
}

export function hasAllPermissions(
  userPermissions: string[] | undefined,
  codenames: (PermissionCodename | string)[]
): boolean {
  const set = new Set(userPermissions ?? []);
  return codenames.every((c) => set.has(c));
}

export function hasRole(userRoles: string[] | undefined, role: string): boolean {
  return (userRoles ?? []).includes(role);
}

export function hasAnyRole(
  userRoles: string[] | undefined,
  roles: string[]
): boolean {
  const set = new Set(userRoles ?? []);
  return roles.some((r) => set.has(r));
}

export function canAccessAdminPortal(
  roles: string[] | undefined,
  permissions: string[] | undefined
): boolean {
  return (
    hasAnyPermission(permissions, [ADMIN_PORTAL_PERMISSION]) ||
    hasAnyRole(roles, [
      "super-admin",
      "admin",
      "manager",
      "warehouse-manager",
      "sales-representative",
      "customer-service",
      "trade-reviewer",
      "staff",
    ])
  );
}
