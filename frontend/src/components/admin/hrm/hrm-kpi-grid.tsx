"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import type { HrmDashboardKpis } from "@/lib/api/admin/hrm-types";

export interface HrmKpiGridProps {
  kpis: HrmDashboardKpis;
}

function HrmKpiGrid({ kpis }: HrmKpiGridProps) {
  const items = [
    { label: "Active headcount", value: String(kpis.headcount) },
    { label: "Clocked in today", value: String(kpis.clockedInToday) },
    { label: "On leave today", value: String(kpis.onLeaveToday) },
    { label: "Pending leave requests", value: String(kpis.pendingLeaveRequests) },
    { label: "Annual leave remaining (days)", value: String(kpis.annualLeaveRemainingDays) },
    { label: "Active asset assignments", value: String(kpis.activeAssetAssignments) },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {items.map((item) => (
        <AdminCard key={item.label} title={item.label}>
          <p className="text-3xl font-bold tracking-tight">{item.value}</p>
        </AdminCard>
      ))}
    </div>
  );
}

export { HrmKpiGrid };
