import type { Metadata } from "next";

import { EmployeesListPageView } from "@/components/admin/pages/hrm-employees-list-page-view";

export const metadata: Metadata = { title: "Employees | HR | Admin | A2Z Tools" };

export default function AdminHrmEmployeesPage() {
  return <EmployeesListPageView />;
}
