import type { ProductStockStatus } from "@/types/product";
import { cn } from "@/lib/utils";

const stockConfig: Record<
  ProductStockStatus,
  { label: string; className: string }
> = {
  in_stock: {
    label: "In stock",
    className: "text-success bg-success-light border-success/20",
  },
  low_stock: {
    label: "Low stock",
    className: "text-warning bg-warning-light border-warning/20",
  },
  back_order: {
    label: "Back order",
    className: "text-muted-foreground bg-neutral-100 border-border",
  },
  out_of_stock: {
    label: "Out of stock",
    className: "text-error bg-error-light border-error/20",
  },
};

export interface ProductStockBadgeProps {
  status: ProductStockStatus;
  className?: string;
  size?: "sm" | "default";
}

function ProductStockBadge({
  status,
  className,
  size = "default",
}: ProductStockBadgeProps) {
  const config = stockConfig[status];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-medium",
        size === "sm" ? "px-2 py-0.5 text-[11px]" : "px-2.5 py-1 text-xs",
        config.className,
        className
      )}
    >
      <span className="size-1.5 shrink-0 rounded-full bg-current" aria-hidden />
      {config.label}
    </span>
  );
}

export { ProductStockBadge, stockConfig };
