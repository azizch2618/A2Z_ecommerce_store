import type { Metadata } from "next";

import { AdminDashboardView } from "@/components/admin/dashboard/admin-dashboard-view";

export const metadata: Metadata = {
  title: "Admin Dashboard | A2Z Tools",
  description: "ERP admin dashboard for A2Z Tools operations, sales, and inventory.",
};

export default function AdminDashboardPage() {
  return <AdminDashboardView />;
}
