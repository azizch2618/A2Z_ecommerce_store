"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { SiteLayout } from "@/components/layout";
import { RouteGuard } from "@/components/rbac/route-guard";
import { hasPermission, Permission, SUPPLIER_PORTAL_ROUTE_PERMISSIONS } from "@/lib/rbac";
import { usePermissions } from "@/hooks/use-permissions";

function SupplierPortalGuard({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { permissions, isLoading } = usePermissions();

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <div className="size-8 animate-spin rounded-full border-2 border-brand-navy border-t-transparent" />
      </div>
    );
  }

  const required =
    SUPPLIER_PORTAL_ROUTE_PERMISSIONS[pathname] ??
    (pathname.startsWith("/supplier-portal") ? Permission.SUPPLIER_PORTAL : null);

  if (required && !hasPermission(permissions, required)) {
    return (
      <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3 p-8 text-center">
        <h1 className="text-2xl font-bold">Access denied</h1>
        <p className="text-sm text-muted-foreground">
          This area is for supplier portal users only.
        </p>
      </div>
    );
  }

  return children;
}

export default function SupplierPortalLayout({
  children,
}: Readonly<{ children: ReactNode }>) {
  return (
    <SiteLayout>
      <RouteGuard>
        <SupplierPortalGuard>{children}</SupplierPortalGuard>
      </RouteGuard>
    </SiteLayout>
  );
}
