import type { AccountDashboardStats } from "@/types/account";
import { cn } from "@/lib/utils";
import {
  FileText,
  Heart,
  Package,
  ShoppingBag,
} from "lucide-react";

export interface AccountStatsGridProps {
  stats: AccountDashboardStats;
  className?: string;
}

const statConfig = [
  {
    key: "totalOrders" as const,
    label: "Total orders",
    icon: ShoppingBag,
    color: "text-brand-blue",
    bg: "bg-brand-blue-light/50 dark:bg-brand-blue-light/10",
  },
  {
    key: "activeOrders" as const,
    label: "Active orders",
    icon: Package,
    color: "text-warning",
    bg: "bg-warning-light/80 dark:bg-warning-light/20",
  },
  {
    key: "wishlistItems" as const,
    label: "Wishlist items",
    icon: Heart,
    color: "text-error",
    bg: "bg-error-light/80 dark:bg-error-light/20",
  },
  {
    key: "savedQuotes" as const,
    label: "Saved quotes",
    icon: FileText,
    color: "text-success",
    bg: "bg-success-light/80 dark:bg-success-light/20",
  },
];

function AccountStatsGrid({ stats, className }: AccountStatsGridProps) {
  return (
    <div
      className={cn(
        "grid gap-4 sm:grid-cols-2 xl:grid-cols-4",
        className
      )}
    >
      {statConfig.map(({ key, label, icon: Icon, color, bg }) => (
        <div
          key={key}
          className="rounded-xl border border-border bg-card p-5 shadow-sm"
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm text-muted-foreground">{label}</p>
              <p className="mt-1 text-3xl font-bold tabular-nums text-foreground">
                {stats[key]}
              </p>
            </div>
            <span
              className={cn(
                "flex size-10 items-center justify-center rounded-lg",
                bg
              )}
            >
              <Icon className={cn("size-5", color)} aria-hidden />
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

export { AccountStatsGrid };
