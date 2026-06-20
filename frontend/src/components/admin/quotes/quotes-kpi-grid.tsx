"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import type { QuoteDashboardKpis } from "@/lib/api/admin/quotes-types";

function formatPct(value: number): string {
  return `${value.toFixed(1)}%`;
}

export interface QuotesKpiGridProps {
  kpis: QuoteDashboardKpis;
}

function QuotesKpiGrid({ kpis }: QuotesKpiGridProps) {
  const items = [
    { label: "Draft quotes", value: kpis.draftQuotes },
    { label: "Pending approval", value: kpis.pendingApproval },
    { label: "Accepted", value: kpis.accepted },
    { label: "Conversion rate", value: formatPct(kpis.conversionRate) },
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

export { QuotesKpiGrid };
