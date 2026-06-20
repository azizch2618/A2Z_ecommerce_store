import type { Metadata } from "next";

import { CrmDashboardPageView } from "@/components/admin/pages/crm-dashboard-page-view";

export const metadata: Metadata = { title: "CRM | Admin | A2Z Tools" };

export default function AdminCrmPage() {
  return <CrmDashboardPageView />;
}
