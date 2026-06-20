import type { Metadata } from "next";

import { ProcurementDashboardPageView } from "@/components/admin/pages/procurement-dashboard-page-view";

export const metadata: Metadata = { title: "Procurement | Admin | A2Z Tools" };

export default function AdminProcurementPage() {
  return <ProcurementDashboardPageView />;
}
