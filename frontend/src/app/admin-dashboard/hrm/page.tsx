import type { Metadata } from "next";

import { HrmDashboardPageView } from "@/components/admin/pages/hrm-dashboard-page-view";

export const metadata: Metadata = { title: "HR | Admin | A2Z Tools" };

export default function AdminHrmPage() {
  return <HrmDashboardPageView />;
}
