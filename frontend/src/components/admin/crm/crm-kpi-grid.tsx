import type { CrmDashboardKpis } from "@/lib/api/admin/types";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(cents / 100);
}

export interface CrmKpiGridProps {
  kpis: CrmDashboardKpis;
}

function CrmKpiGrid({ kpis }: CrmKpiGridProps) {
  const cards = [
    { label: "Total leads", value: String(kpis.totalLeads) },
    { label: "Open opportunities", value: String(kpis.openOpportunities) },
    { label: "Conversion rate", value: `${kpis.conversionRate}%` },
    { label: "Revenue forecast", value: formatAud(kpis.revenueForecastCents) },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-xl border border-border bg-card p-5 shadow-sm"
        >
          <p className="text-sm font-medium text-muted-foreground">{card.label}</p>
          <p className="mt-2 text-2xl font-bold tabular-nums tracking-tight">{card.value}</p>
        </div>
      ))}
    </div>
  );
}

export { CrmKpiGrid };
