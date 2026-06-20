import type { Metadata } from "next";

import { WmsDashboardPageView } from "@/components/admin/pages/wms-dashboard-page-view";

export const metadata: Metadata = { title: "WMS | Admin | A2Z Tools" };

export default function WmsDashboardPage() {
  return <WmsDashboardPageView />;
}
