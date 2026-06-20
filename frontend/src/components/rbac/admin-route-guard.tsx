"use client";

import type { ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useCanAccessAdmin, usePermissions } from "@/hooks/use-permissions";
import {
  getRequiredPermissionForPath,
  hasPermission,
  type PermissionCodename,
} from "@/lib/rbac";
import { isAdminDemoEnabled } from "@/lib/security/admin-demo";
import { hasAuthTokens } from "@/lib/api/auth/token-storage";

const ADMIN_DEMO_MODE = isAdminDemoEnabled();

export interface AdminRouteGuardProps {
  children: ReactNode;
  pathname?: string;
}

function AccessDenied() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3 p-8 text-center">
      <h1 className="text-2xl font-bold text-foreground">Access denied</h1>
      <p className="max-w-md text-sm text-muted-foreground">
        You do not have permission to view this page. Contact your administrator
        if you believe this is an error.
      </p>
    </div>
  );
}

function AdminRouteGuard({ children, pathname }: AdminRouteGuardProps) {
  const router = useRouter();
  const { permissions, isLoading, user } = usePermissions();
  const canAccessAdmin = useCanAccessAdmin();

  const requiredPermission: PermissionCodename | null = pathname
    ? getRequiredPermissionForPath(pathname)
    : null;

  const hasRoutePermission =
    !requiredPermission || hasPermission(permissions, requiredPermission);

  useEffect(() => {
    if (isLoading) return;
    const hasTokens = hasAuthTokens();
    if (!hasTokens && !ADMIN_DEMO_MODE) {
      router.replace("/login?redirect=/admin-dashboard");
    }
  }, [isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="size-8 animate-spin rounded-full border-2 border-brand-navy border-t-transparent" />
      </div>
    );
  }

  if (!hasAuthTokens() && !ADMIN_DEMO_MODE) {
    return null;
  }

  if (user && !canAccessAdmin) {
    return <AccessDenied />;
  }

  if (!hasRoutePermission) {
    return <AccessDenied />;
  }

  return children;
}

export { AdminRouteGuard };
