import { cn } from "@/lib/utils";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

import type { KpiMetric } from "@/lib/api/admin/types";

export interface KpiCardProps {
  metric: KpiMetric;
  className?: string;
}

function KpiCard({ metric, className }: KpiCardProps) {
  const TrendIcon =
    metric.trend === "up" ? ArrowUpRight : metric.trend === "down" ? ArrowDownRight : Minus;

  const trendColor =
    metric.trend === "up"
      ? "text-success"
      : metric.trend === "down"
        ? "text-error"
        : "text-muted-foreground";

  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-card p-5 shadow-sm transition-shadow hover:shadow-md",
        className
      )}
    >
      <p className="text-sm font-medium text-muted-foreground">{metric.label}</p>
      <p className="mt-2 text-2xl font-bold tabular-nums tracking-tight text-foreground md:text-3xl">
        {metric.value}
      </p>
      <div className={cn("mt-2 flex items-center gap-1 text-sm font-medium", trendColor)}>
        <TrendIcon className="size-4" aria-hidden />
        <span>
          {metric.growthPercent > 0 ? "+" : ""}
          {metric.growthPercent}%
        </span>
        <span className="text-muted-foreground font-normal">vs last period</span>
      </div>
    </div>
  );
}

export { KpiCard };
