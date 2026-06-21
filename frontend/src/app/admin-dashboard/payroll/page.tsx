import type { Metadata } from "next";

import { PayrollDashboardPageView } from "@/components/admin/pages/payroll-dashboard-page-view";

export const metadata: Metadata = { title: "Payroll | Admin | A2Z Tools" };

export default function AdminPayrollPage() {
  return <PayrollDashboardPageView />;
}
