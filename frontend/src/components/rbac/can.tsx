"use client";

import type { ReactNode } from "react";

import {
  useHasAllPermissions,
  useHasAnyPermission,
  useHasPermission,
  useHasAnyRole,
  useHasRole,
} from "@/hooks/use-permissions";
import type { PermissionCodename } from "@/lib/rbac";

export interface CanProps {
  permission?: PermissionCodename | string;
  permissions?: (PermissionCodename | string)[];
  requireAll?: boolean;
  role?: string;
  roles?: string[];
  fallback?: ReactNode;
  children: ReactNode;
}

/**
 * Conditionally render children based on RBAC permissions or roles.
 *
 * @example
 * <Can permission={Permission.ORDERS_MANAGE}>
 *   <Button>Cancel order</Button>
 * </Can>
 */
function Can({
  permission,
  permissions,
  requireAll = false,
  role,
  roles,
  fallback = null,
  children,
}: CanProps) {
  const hasSingle = useHasPermission(permission ?? "");
  const hasAny = useHasAnyPermission(permissions ?? []);
  const hasAll = useHasAllPermissions(permissions ?? []);
  const hasSingleRole = useHasRole(role ?? "");
  const hasAnyRoleCheck = useHasAnyRole(roles ?? []);

  let allowed = true;

  if (permission) {
    allowed = allowed && hasSingle;
  }
  if (permissions && permissions.length > 0) {
    allowed = allowed && (requireAll ? hasAll : hasAny);
  }
  if (role) {
    allowed = allowed && hasSingleRole;
  }
  if (roles && roles.length > 0) {
    allowed = allowed && hasAnyRoleCheck;
  }

  return allowed ? children : fallback;
}

export { Can };
