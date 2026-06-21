"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import type { PayrollDashboardKpis } from "@/lib/api/admin/payroll-types";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

export interface PayrollKpiGridProps {
  kpis: PayrollDashboardKpis;
}

function PayrollKpiGrid({ kpis }: PayrollKpiGridProps) {
  const items = [
    { label: "Total payroll YTD", value: formatAud(kpis.totalPayrollYtdCents) },
    { label: "Gross payroll YTD", value: formatAud(kpis.totalGrossYtdCents) },
    { label: "Posted runs (FY)", value: String(kpis.postedRunsCount) },
    { label: "Pending approval", value: String(kpis.pendingApprovalCount) },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <AdminCard key={item.label} title={item.label}>
          <p className="text-3xl font-bold tracking-tight">{item.value}</p>
        </AdminCard>
      ))}
    </div>
  );
}

export { PayrollKpiGrid };
