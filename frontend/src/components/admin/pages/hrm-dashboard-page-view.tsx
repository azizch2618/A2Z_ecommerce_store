"use client";

import Link from "next/link";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { EmployeesTable } from "@/components/admin/hrm/employees-table";
import { HrmKpiGrid } from "@/components/admin/hrm/hrm-kpi-grid";
import { LeaveRequestsTable } from "@/components/admin/hrm/leave-requests-table";
import { OrgStructureTree } from "@/components/admin/hrm/org-structure-tree";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  useAssetAssignments,
  useEmployees,
  useHrmDashboard,
  useLeaveRequests,
  useOrgStructure,
} from "@/lib/api/admin/hrm-hooks";

function HrmDashboardPageView() {
  const dashboard = useHrmDashboard();
  const employees = useEmployees({ status: "active" });
  const leaveRequests = useLeaveRequests();
  const orgStructure = useOrgStructure();
  const assetAssignments = useAssetAssignments();

  const isLoading =
    dashboard.isLoading ||
    employees.isLoading ||
    leaveRequests.isLoading ||
    orgStructure.isLoading ||
    assetAssignments.isLoading;

  const isError =
    dashboard.isError ||
    employees.isError ||
    leaveRequests.isError ||
    orgStructure.isError ||
    assetAssignments.isError;

  return (
    <AdminListPage
      title="Human Resources"
      description="Employees, attendance, leave, assets, and organizational structure."
      isLoading={isLoading}
      isError={isError}
      actions={
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/hrm/employees">All employees</Link>
        </Button>
      }
    >
      {dashboard.data ? <HrmKpiGrid kpis={dashboard.data} /> : null}

      <div className="grid gap-6 xl:grid-cols-2">
        <AdminCard title="Active employees">
          <EmployeesTable employees={(employees.data ?? []).slice(0, 10)} />
        </AdminCard>

        <AdminCard title="Leave requests">
          <LeaveRequestsTable requests={(leaveRequests.data ?? []).slice(0, 10)} />
        </AdminCard>
      </div>

      <AdminCard title="Active asset assignments">
        {(assetAssignments.data ?? []).length === 0 ? (
          <p className="text-sm text-muted-foreground">No assets currently assigned.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Asset</TableHead>
                <TableHead>Employee</TableHead>
                <TableHead>Issued</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(assetAssignments.data ?? []).slice(0, 10).map((row) => (
                <TableRow key={row.id}>
                  <TableCell>
                    {row.assetNumber} — {row.assetName}
                  </TableCell>
                  <TableCell>{row.employeeName}</TableCell>
                  <TableCell>{row.issuedAt.slice(0, 10)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </AdminCard>

      {orgStructure.data ? <OrgStructureTree org={orgStructure.data} /> : null}
    </AdminListPage>
  );
}

export { HrmDashboardPageView };
