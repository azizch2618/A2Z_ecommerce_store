"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import type { ProcurementDashboardKpis } from "@/lib/api/admin/procurement-types";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

function formatPct(value: number): string {
  return `${value.toFixed(1)}%`;
}

export interface ProcurementKpiGridProps {
  kpis: ProcurementDashboardKpis;
}

function ProcurementKpiGrid({ kpis }: ProcurementKpiGridProps) {
  const items = [
    { label: "Open requisitions", value: String(kpis.openRequisitions) },
    { label: "Open purchase orders", value: String(kpis.openPurchaseOrders) },
    { label: "Procurement spend", value: formatAud(kpis.procurementSpendCents) },
    { label: "On-time delivery", value: formatPct(kpis.onTimeDeliveryPct) },
    { label: "Avg lead time", value: `${kpis.avgLeadTimeDays.toFixed(1)} days` },
    { label: "Order accuracy", value: formatPct(kpis.orderAccuracyPct) },
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

export { ProcurementKpiGrid };
