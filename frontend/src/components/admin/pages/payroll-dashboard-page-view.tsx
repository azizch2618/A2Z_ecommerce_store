"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { PayrollKpiGrid } from "@/components/admin/payroll/payroll-kpi-grid";
import { PayrollPeriodsTable } from "@/components/admin/payroll/payroll-periods-table";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { usePayrollDashboard, usePayrollPeriods } from "@/lib/api/admin/payroll-hooks";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

function PayrollDashboardPageView() {
  const dashboard = usePayrollDashboard();
  const periods = usePayrollPeriods();

  return (
    <AdminListPage
      title="Payroll"
      description="Pay runs, salary structures, payslips, and GL integration."
      isLoading={dashboard.isLoading || periods.isLoading}
      isError={dashboard.isError || periods.isError}
    >
      {dashboard.data ? <PayrollKpiGrid kpis={dashboard.data} /> : null}

      <div className="grid gap-6 xl:grid-cols-2">
        <AdminCard title="Payroll periods">
          <PayrollPeriodsTable periods={(periods.data ?? []).slice(0, 10)} />
        </AdminCard>

        <AdminCard title="Upcoming pay runs">
          {(dashboard.data?.upcomingRuns ?? []).length === 0 ? (
            <p className="text-sm text-muted-foreground">No upcoming payroll runs.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Run</TableHead>
                  <TableHead>Pay date</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {dashboard.data!.upcomingRuns.map((run) => (
                  <TableRow key={run.id}>
                    <TableCell>
                      {run.periodNumber} — {run.name}
                    </TableCell>
                    <TableCell>{run.payDate}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {run.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </AdminCard>
      </div>

      <AdminCard title="Department cost (YTD)">
        {(dashboard.data?.departmentCosts ?? []).length === 0 ? (
          <p className="text-sm text-muted-foreground">No posted payroll data yet.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Department</TableHead>
                <TableHead>Headcount</TableHead>
                <TableHead className="text-right">Total net pay</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {dashboard.data!.departmentCosts.map((row) => (
                <TableRow key={row.departmentName}>
                  <TableCell>{row.departmentName}</TableCell>
                  <TableCell>{row.headcount}</TableCell>
                  <TableCell className="text-right">{formatAud(row.totalCents)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </AdminCard>
    </AdminListPage>
  );
}

export { PayrollDashboardPageView };
