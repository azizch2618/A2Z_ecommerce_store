import type { KpiMetric } from "@/lib/api/admin/types";
import { cn } from "@/lib/utils";

import { KpiCard } from "./kpi-card";

export interface KpiGridProps {
  metrics: KpiMetric[];
  className?: string;
}

function KpiGrid({ metrics, className }: KpiGridProps) {
  return (
    <div
      className={cn(
        "grid gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4",
        className
      )}
    >
      {metrics.map((metric) => (
        <KpiCard key={metric.id} metric={metric} />
      ))}
    </div>
  );
}

export { KpiGrid };
