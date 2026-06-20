import type { Metadata } from "next";

import { ReportsPageView } from "@/components/admin/pages/reports-page-view";

export const metadata: Metadata = { title: "Reports | Admin | A2Z Tools" };

export default function AdminReportsPage() {
  return <ReportsPageView />;
}
