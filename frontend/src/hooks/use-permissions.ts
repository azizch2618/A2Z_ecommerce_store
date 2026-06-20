"use client";

import { useMemo } from "react";

import { useAuth } from "@/lib/api/hooks/use-auth";
import { isAdminDemoEnabled } from "@/lib/security/admin-demo";
import { ALL_PERMISSIONS, type PermissionCodename } from "@/lib/rbac/permissions";
import {
  canAccessAdminPortal,
  hasAllPermissions,
  hasAnyPermission,
  hasAnyRole,
  hasPermission,
  hasRole,
} from "@/lib/rbac/access";
import { ADMIN_PORTAL_ROLES, getPrimaryRoleLabel } from "@/lib/rbac/roles";

const ADMIN_DEMO_MODE = isAdminDemoEnabled();

function useDemoPermissions(): string[] | null {
  if (!ADMIN_DEMO_MODE) return null;
  return ALL_PERMISSIONS;
}

function useDemoRoles(): string[] | null {
  if (!ADMIN_DEMO_MODE) return null;
  return ["manager"];
}

export function usePermissions() {
  const { user, isLoading } = useAuth();
  const demoPerms = useDemoPermissions();

  const permissions = useMemo(
    () => user?.permissions ?? demoPerms ?? [],
    [user?.permissions, demoPerms]
  );

  return { permissions, isLoading, user };
}

export function useRoles() {
  const { user, isLoading } = useAuth();
  const demoRoles = useDemoRoles();

  const roles = useMemo(
    () => user?.roles ?? demoRoles ?? [],
    [user?.roles, demoRoles]
  );

  const roleLabel = useMemo(() => getPrimaryRoleLabel(roles), [roles]);

  return { roles, roleLabel, isLoading, user };
}

export function useHasPermission(codename: PermissionCodename | string) {
  const { permissions } = usePermissions();
  return hasPermission(permissions, codename);
}

export function useHasAnyPermission(
  codenames: (PermissionCodename | string)[]
) {
  const { permissions } = usePermissions();
  return hasAnyPermission(permissions, codenames);
}

export function useHasAllPermissions(
  codenames: (PermissionCodename | string)[]
) {
  const { permissions } = usePermissions();
  return hasAllPermissions(permissions, codenames);
}

export function useHasRole(role: string) {
  const { roles } = useRoles();
  return hasRole(roles, role);
}

export function useHasAnyRole(roleList: string[]) {
  const { roles } = useRoles();
  return hasAnyRole(roles, roleList);
}

export function useCanAccessAdmin() {
  const { permissions } = usePermissions();
  const { roles } = useRoles();
  return canAccessAdminPortal(roles, permissions);
}

export function useIsInternalStaff() {
  const { roles } = useRoles();
  return hasAnyRole(roles, ADMIN_PORTAL_ROLES);
}
