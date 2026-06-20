import type { OrderStatus } from "@/lib/api/admin/types";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

const statusConfig: Record<
  OrderStatus,
  { label: string; variant: "default" | "secondary" | "success" | "warning" | "destructive" | "trade" }
> = {
  pending: { label: "Pending", variant: "warning" },
  awaiting_payment: { label: "Awaiting payment", variant: "warning" },
  paid: { label: "Paid", variant: "success" },
  packed: { label: "Packed", variant: "default" },
  shipped: { label: "Shipped", variant: "trade" },
  delivered: { label: "Delivered", variant: "success" },
  cancelled: { label: "Cancelled", variant: "destructive" },
  refunded: { label: "Refunded", variant: "secondary" },
};

export interface OrderStatusBadgeProps {
  status: OrderStatus;
  className?: string;
}

function OrderStatusBadge({ status, className }: OrderStatusBadgeProps) {
  const config = statusConfig[status];
  return (
    <Badge variant={config.variant} className={cn("capitalize", className)}>
      {config.label}
    </Badge>
  );
}

export { OrderStatusBadge };
