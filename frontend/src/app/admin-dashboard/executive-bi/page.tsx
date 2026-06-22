import type { Metadata } from "next";

import { ExecutiveBiDashboardPageView } from "@/components/admin/pages/executive-bi-dashboard-page-view";

export const metadata: Metadata = { title: "Executive BI | Admin | A2Z Tools" };

export default function AdminExecutiveBiPage() {
  return <ExecutiveBiDashboardPageView />;
}
