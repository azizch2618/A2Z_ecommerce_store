"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";

import { AdminShell } from "@/components/admin/layout/admin-shell";
import { AdminRouteGuard } from "@/components/rbac/admin-route-guard";

function AdminDashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <AdminRouteGuard pathname={pathname}>
      <AdminShell>{children}</AdminShell>
    </AdminRouteGuard>
  );
}

export default AdminDashboardLayout;
