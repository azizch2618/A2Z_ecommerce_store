"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { SiteLayout } from "@/components/layout";
import { RouteGuard } from "@/components/rbac/route-guard";
import { usePermissions } from "@/hooks/use-permissions";
import { hasPermission, Permission, WAREHOUSE_MOBILE_ROUTE_PERMISSIONS } from "@/lib/rbac";

function MobileGuard({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { permissions, isLoading } = usePermissions();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="size-8 animate-spin rounded-full border-2 border-brand-navy border-t-transparent" />
      </div>
    );
  }

  const required =
    WAREHOUSE_MOBILE_ROUTE_PERMISSIONS[pathname] ??
    (pathname.startsWith("/warehouse-mobile") ? Permission.WMS_EXECUTE : null);

  if (required && !hasPermission(permissions, required)) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 p-8 text-center">
        <h1 className="text-xl font-bold">Access denied</h1>
        <p className="text-sm text-muted-foreground">Warehouse operator access required.</p>
      </div>
    );
  }

  return children;
}

export default function WarehouseMobileLayout({ children }: { children: ReactNode }) {
  return (
    <SiteLayout>
      <RouteGuard>
        <MobileGuard>{children}</MobileGuard>
      </RouteGuard>
    </SiteLayout>
  );
}
