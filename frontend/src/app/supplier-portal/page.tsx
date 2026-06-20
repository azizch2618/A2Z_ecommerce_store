import type { Metadata } from "next";

import { SupplierPortalDashboardView } from "@/components/supplier-portal/supplier-portal-dashboard-view";

export const metadata: Metadata = { title: "Supplier Portal | A2Z Tools" };

export default function SupplierPortalPage() {
  return <SupplierPortalDashboardView />;
}
