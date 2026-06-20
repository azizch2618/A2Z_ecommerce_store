"use client";

import { useState } from "react";
import { MoreHorizontal, Package, Truck, CheckCircle, XCircle, RotateCcw } from "lucide-react";
import { toast } from "sonner";

import type { AdminOrder, OrderStatus } from "@/lib/api/admin/types";
import { OrderStatusBadge } from "@/components/admin/shared/order-status-badge";
import {
  useOrderCancel,
  useOrderDeliver,
  useOrderPack,
  useOrderRefund,
  useOrderShip,
} from "@/lib/api/admin/hooks";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function formatAud(cents: number) {
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
  }).format(cents / 100);
}

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en-AU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(iso));
}

const PACKABLE: OrderStatus[] = ["paid", "pending", "awaiting_payment"];
const SHIPPABLE: OrderStatus[] = ["packed"];
const DELIVERABLE: OrderStatus[] = ["shipped"];
const CANCELLABLE: OrderStatus[] = ["pending", "awaiting_payment", "paid", "packed"];
const REFUNDABLE: OrderStatus[] = ["paid", "packed", "shipped", "delivered"];

export interface RecentOrdersTableProps {
  orders: AdminOrder[];
  showActions?: boolean;
}

function OrderActionsMenu({ order }: { order: AdminOrder }) {
  const pack = useOrderPack();
  const ship = useOrderShip();
  const deliver = useOrderDeliver();
  const cancel = useOrderCancel();
  const refund = useOrderRefund();
  const busy =
    pack.isPending || ship.isPending || deliver.isPending || cancel.isPending || refund.isPending;

  const run = (
    label: string,
    fn: () => Promise<unknown>
  ) => {
    void fn()
      .then(() => toast.success(`${label}: ${order.orderNumber}`))
      .catch(() => toast.error(`${label} failed`));
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="size-8" disabled={busy} aria-label="Order actions">
          <MoreHorizontal className="size-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {PACKABLE.includes(order.status) ? (
          <DropdownMenuItem onClick={() => run("Packed", () => pack.mutateAsync(order.id))}>
            <Package className="mr-2 size-4" />
            Pack
          </DropdownMenuItem>
        ) : null}
        {SHIPPABLE.includes(order.status) ? (
          <DropdownMenuItem
            onClick={() => run("Shipped", () => ship.mutateAsync({ orderId: order.id }))}
          >
            <Truck className="mr-2 size-4" />
            Ship
          </DropdownMenuItem>
        ) : null}
        {DELIVERABLE.includes(order.status) ? (
          <DropdownMenuItem onClick={() => run("Delivered", () => deliver.mutateAsync(order.id))}>
            <CheckCircle className="mr-2 size-4" />
            Deliver
          </DropdownMenuItem>
        ) : null}
        {(CANCELLABLE.includes(order.status) || REFUNDABLE.includes(order.status)) && (
          <DropdownMenuSeparator />
        )}
        {CANCELLABLE.includes(order.status) ? (
          <DropdownMenuItem
            className="text-destructive"
            onClick={() => run("Cancelled", () => cancel.mutateAsync({ orderId: order.id }))}
          >
            <XCircle className="mr-2 size-4" />
            Cancel
          </DropdownMenuItem>
        ) : null}
        {REFUNDABLE.includes(order.status) ? (
          <DropdownMenuItem
            className="text-destructive"
            onClick={() => run("Refunded", () => refund.mutateAsync({ orderId: order.id }))}
          >
            <RotateCcw className="mr-2 size-4" />
            Refund
          </DropdownMenuItem>
        ) : null}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function RecentOrdersTable({ orders, showActions = true }: RecentOrdersTableProps) {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const filtered =
    statusFilter === "all" ? orders : orders.filter((o) => o.status === statusFilter);

  return (
    <div>
      {showActions ? (
        <div className="flex flex-wrap gap-2 border-b border-border px-4 py-3">
          {["all", "pending", "paid", "packed", "shipped", "delivered", "cancelled", "refunded"].map(
            (s) => (
              <Button
                key={s}
                size="sm"
                variant={statusFilter === s ? "default" : "outline"}
                onClick={() => setStatusFilter(s)}
                className="capitalize"
              >
                {s === "all" ? "All" : s.replace("_", " ")}
              </Button>
            )
          )}
        </div>
      ) : null}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Order</TableHead>
            <TableHead>Customer</TableHead>
            <TableHead className="text-right">Amount</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Date</TableHead>
            {showActions ? <TableHead className="text-right">Actions</TableHead> : null}
          </TableRow>
        </TableHeader>
        <TableBody>
          {filtered.map((order) => (
            <TableRow key={order.id}>
              <TableCell className="font-mono text-sm font-medium">{order.orderNumber}</TableCell>
              <TableCell>
                <p className="font-medium">{order.customerName}</p>
                <p className="text-xs text-muted-foreground">{order.customerEmail}</p>
              </TableCell>
              <TableCell className="text-right font-medium tabular-nums">
                {formatAud(order.amountCents)}
              </TableCell>
              <TableCell>
                <OrderStatusBadge status={order.status} />
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {formatDate(order.placedAt)}
              </TableCell>
              {showActions ? (
                <TableCell className="text-right">
                  <OrderActionsMenu order={order} />
                </TableCell>
              ) : null}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

export { RecentOrdersTable };
