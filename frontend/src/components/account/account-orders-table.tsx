import Link from "next/link";
import { ArrowRight, Package } from "lucide-react";

import type { AccountOrder } from "@/types/account";
import { formatAud } from "@/lib/cart";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const statusStyles = {
  processing: "bg-warning-light text-warning dark:bg-warning-light/20",
  shipped: "bg-brand-blue-light text-brand-blue dark:bg-brand-blue-light/15",
  delivered: "bg-success-light text-success dark:bg-success-light/20",
  cancelled: "bg-error-light text-error dark:bg-error-light/20",
} as const;

export interface AccountOrdersTableProps {
  orders: AccountOrder[];
  limit?: number;
  showViewAll?: boolean;
  className?: string;
}

function formatOrderDate(iso: string) {
  return new Intl.DateTimeFormat("en-AU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(iso));
}

function AccountOrdersTable({
  orders,
  limit,
  showViewAll = false,
  className,
}: AccountOrdersTableProps) {
  const displayOrders = limit ? orders.slice(0, limit) : orders;

  if (displayOrders.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-12 text-center">
        <Package className="size-10 text-muted-foreground" aria-hidden />
        <p className="mt-3 text-sm font-medium text-foreground">No orders yet</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Browse the catalogue to place your first order.
        </p>
        <Button asChild className="mt-4">
          <Link href="/products">Shop products</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Order</TableHead>
              <TableHead className="hidden sm:table-cell">Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="hidden md:table-cell">Items</TableHead>
              <TableHead className="text-right">Total</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {displayOrders.map((order) => (
              <TableRow key={order.id}>
                <TableCell className="font-mono text-sm font-medium">
                  <Link
                    href={`/account/orders/${order.id}`}
                    className="text-brand-blue hover:underline"
                  >
                    {order.orderNumber}
                  </Link>
                </TableCell>
                <TableCell className="hidden text-muted-foreground sm:table-cell">
                  {formatOrderDate(order.date)}
                </TableCell>
                <TableCell>
                  <Badge
                    variant="outline"
                    className={cn(
                      "border-0 capitalize",
                      statusStyles[order.status]
                    )}
                  >
                    {order.status}
                  </Badge>
                </TableCell>
                <TableCell className="hidden text-muted-foreground md:table-cell">
                  {order.itemCount}
                </TableCell>
                <TableCell className="text-right font-medium tabular-nums">
                  {formatAud(order.totalIncGst)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {showViewAll ? (
        <div className="flex justify-end">
          <Button asChild variant="outline" size="sm" className="gap-2">
            <Link href="/account/orders">
              View all orders
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        </div>
      ) : null}
    </div>
  );
}

export { AccountOrdersTable };
