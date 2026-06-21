"use client";

import Link from "next/link";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { EmployeesTable } from "@/components/admin/hrm/employees-table";
import { Button } from "@/components/ui/button";
import { useEmployees } from "@/lib/api/admin/hrm-hooks";

function EmployeesListPageView() {
  const employees = useEmployees();

  return (
    <AdminListPage
      title="Employees"
      description="Workforce directory — personal details, job assignments, and employment status."
      isLoading={employees.isLoading}
      isError={employees.isError}
      actions={
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/hrm">Back to HR dashboard</Link>
        </Button>
      }
    >
      <AdminCard title="All employees">
        <EmployeesTable employees={employees.data ?? []} />
      </AdminCard>
    </AdminListPage>
  );
}

export { EmployeesListPageView };
