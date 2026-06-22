"use client";

import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  Circle,
  Download,
  Loader2,
  MoreHorizontal,
  Package,
  RotateCcw,
  Truck,
  XCircle,
} from "lucide-react";
import { toast } from "sonner";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { OrderStatusBadge } from "@/components/admin/shared/order-status-badge";
import { Badge } from "@/components/ui/badge";
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
import {
  useAdminOrderDetail,
  useOrderCancel,
  useOrderDeliver,
  useOrderPack,
  useOrderRefund,
  useOrderShip,
} from "@/lib/api/admin/hooks";
import { orderInvoiceUrl } from "@/lib/api/admin/order-service";
import type { OrderStatus } from "@/lib/api/admin/types";
import type { OrderDetail } from "@/lib/api/types/order";
import { cn } from "@/lib/utils";

function formatAud(cents: number) {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

function formatDate(value: string | null | undefined) {
  if (!value) return null;
  return new Intl.DateTimeFormat("en-AU", { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(value)
  );
}

function formatAddress(address: {
  line1: string;
  line2?: string | null;
  suburb: string;
  state: string;
  postcode: string;
  country?: string;
}) {
  const lines = [
    address.line1,
    address.line2,
    `${address.suburb} ${address.state} ${address.postcode}`,
    address.country && address.country !== "AU" ? address.country : undefined,
  ].filter(Boolean);
  return lines.join(", ");
}

type TimelineStep = {
  key: string;
  label: string;
  at: string | null | undefined;
};

function buildTimeline(order: OrderDetail): TimelineStep[] {
  if (order.status === "cancelled") {
    return [
      { key: "placed", label: "Order placed", at: order.placed_at },
      { key: "cancelled", label: "Cancelled", at: order.cancelled_at },
    ];
  }

  if (order.status === "refunded") {
    return [
      { key: "placed", label: "Order placed", at: order.placed_at },
      { key: "paid", label: "Payment received", at: order.paid_at },
      { key: "refunded", label: "Refunded", at: order.cancelled_at },
    ];
  }

  return [
    { key: "placed", label: "Order placed", at: order.placed_at },
    { key: "paid", label: "Payment received", at: order.paid_at },
    { key: "packed", label: "Packed", at: order.packed_at },
    { key: "shipped", label: "Shipped", at: order.shipped_at },
    { key: "delivered", label: "Delivered", at: order.delivered_at },
  ];
}

function OrderTimeline({ order }: { order: OrderDetail }) {
  const steps = buildTimeline(order);

  return (
    <ol className="space-y-4">
      {steps.map((step, index) => {
        const completed = Boolean(step.at);
        const isLast = index === steps.length - 1;
        const isCurrent = completed && (isLast || !steps[index + 1]?.at);

        return (
          <li key={step.key} className="flex gap-3">
            <div className="flex flex-col items-center">
              {completed ? (
                <CheckCircle2
                  className={cn(
                    "size-5 shrink-0",
                    isCurrent ? "text-primary" : "text-muted-foreground"
                  )}
                />
              ) : (
                <Circle className="size-5 shrink-0 text-muted-foreground/40" />
              )}
              {!isLast ? <div className="mt-1 w-px flex-1 bg-border" /> : null}
            </div>
            <div className={cn("pb-4", isLast && "pb-0")}>
              <p
                className={cn(
                  "text-sm font-medium",
                  completed ? "text-foreground" : "text-muted-foreground"
                )}
              >
                {step.label}
              </p>
              <p className="text-xs text-muted-foreground">
                {completed ? formatDate(step.at) : "Pending"}
              </p>
            </div>
          </li>
        );
      })}
    </ol>
  );
}

const PACKABLE: OrderStatus[] = ["paid", "pending", "awaiting_payment"];
const SHIPPABLE: OrderStatus[] = ["packed"];
const DELIVERABLE: OrderStatus[] = ["shipped"];
const CANCELLABLE: OrderStatus[] = ["pending", "awaiting_payment", "paid", "packed"];
const REFUNDABLE: OrderStatus[] = ["paid", "packed", "shipped", "delivered"];

function OrderDetailActions({ orderId, status }: { orderId: string; status: OrderStatus }) {
  const pack = useOrderPack();
  const ship = useOrderShip();
  const deliver = useOrderDeliver();
  const cancel = useOrderCancel();
  const refund = useOrderRefund();
  const busy =
    pack.isPending || ship.isPending || deliver.isPending || cancel.isPending || refund.isPending;

  const run = (label: string, fn: () => Promise<unknown>) => {
    void fn()
      .then(() => toast.success(label))
      .catch(() => toast.error(`${label} failed`));
  };

  const hasActions =
    PACKABLE.includes(status) ||
    SHIPPABLE.includes(status) ||
    DELIVERABLE.includes(status) ||
    CANCELLABLE.includes(status) ||
    REFUNDABLE.includes(status);

  if (!hasActions) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" disabled={busy}>
          <MoreHorizontal className="mr-2 size-4" />
          Actions
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {PACKABLE.includes(status) ? (
          <DropdownMenuItem onClick={() => run("Order packed", () => pack.mutateAsync(orderId))}>
            <Package className="mr-2 size-4" />
            Pack
          </DropdownMenuItem>
        ) : null}
        {SHIPPABLE.includes(status) ? (
          <DropdownMenuItem
            onClick={() => run("Order shipped", () => ship.mutateAsync({ orderId }))}
          >
            <Truck className="mr-2 size-4" />
            Ship
          </DropdownMenuItem>
        ) : null}
        {DELIVERABLE.includes(status) ? (
          <DropdownMenuItem onClick={() => run("Order delivered", () => deliver.mutateAsync(orderId))}>
            <CheckCircle2 className="mr-2 size-4" />
            Deliver
          </DropdownMenuItem>
        ) : null}
        {(CANCELLABLE.includes(status) || REFUNDABLE.includes(status)) && (
          <DropdownMenuSeparator />
        )}
        {CANCELLABLE.includes(status) ? (
          <DropdownMenuItem
            className="text-destructive"
            onClick={() => run("Order cancelled", () => cancel.mutateAsync({ orderId }))}
          >
            <XCircle className="mr-2 size-4" />
            Cancel
          </DropdownMenuItem>
        ) : null}
        {REFUNDABLE.includes(status) ? (
          <DropdownMenuItem
            className="text-destructive"
            onClick={() => run("Order refunded", () => refund.mutateAsync({ orderId }))}
          >
            <RotateCcw className="mr-2 size-4" />
            Refund
          </DropdownMenuItem>
        ) : null}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export interface OrderDetailPageViewProps {
  orderId: string;
}

function OrderDetailPageView({ orderId }: OrderDetailPageViewProps) {
  const { data: order, isLoading, isError } = useAdminOrderDetail(orderId);

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !order) {
    return (
      <div className="space-y-4">
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/orders">
            <ArrowLeft className="mr-2 size-4" />
            Back to orders
          </Link>
        </Button>
        <p className="text-muted-foreground">Order not found.</p>
      </div>
    );
  }

  const shippingIncGst =
    order.totals.shipping_ex_gst_cents + order.totals.shipping_gst_cents;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Button variant="ghost" size="sm" asChild className="mb-2 -ml-2">
            <Link href="/admin-dashboard/orders">
              <ArrowLeft className="mr-1 size-4" />
              Orders
            </Link>
          </Button>
          <h1 className="font-mono text-2xl font-bold tracking-tight">{order.order_number}</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Placed {formatDate(order.placed_at) ?? "—"}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <OrderStatusBadge status={order.status} />
            <Badge variant="outline" className="capitalize">
              Payment: {order.payment_status.replace("_", " ")}
            </Badge>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" asChild>
            <a href={orderInvoiceUrl(orderId)} target="_blank" rel="noopener noreferrer">
              <Download className="mr-2 size-4" />
              Download invoice
            </a>
          </Button>
          <OrderDetailActions orderId={orderId} status={order.status} />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <AdminCard title="Customer">
          {order.customer_id ? (
            <Link
              href={`/admin-dashboard/customers/${order.customer_id}`}
              className="font-medium text-primary hover:underline"
            >
              {order.customer_name ?? "Customer"}
            </Link>
          ) : (
            <p className="font-medium">{order.customer_name ?? "Guest"}</p>
          )}
          {order.customer_email ? (
            <p className="mt-1 text-sm text-muted-foreground">{order.customer_email}</p>
          ) : null}
          {order.po_number ? (
            <p className="mt-2 text-sm">
              <span className="text-muted-foreground">PO: </span>
              {order.po_number}
            </p>
          ) : null}
        </AdminCard>

        <AdminCard title="Payment">
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">Status</dt>
              <dd className="font-medium capitalize">{order.payment_status.replace("_", " ")}</dd>
            </div>
            {order.payment ? (
              <div className="flex justify-between gap-4">
                <dt className="text-muted-foreground">Payment ID</dt>
                <dd className="font-mono text-xs">{order.payment.id.slice(0, 8)}…</dd>
              </div>
            ) : null}
            <div className="flex justify-between gap-4">
              <dt className="text-muted-foreground">Total</dt>
              <dd className="font-medium tabular-nums">
                {formatAud(order.totals.total_inc_gst_cents)}
              </dd>
            </div>
          </dl>
        </AdminCard>

        <AdminCard title="Shipping">
          <p className="text-sm">{formatAddress(order.shipping_address)}</p>
          {order.shipping_method?.name ? (
            <p className="mt-2 text-sm text-muted-foreground">
              Method: {order.shipping_method.name}
            </p>
          ) : null}
          {order.shipments && order.shipments.length > 0 ? (
            <div className="mt-3 space-y-2 border-t border-border pt-3 text-sm">
              {order.shipments.map((shipment) => (
                <div key={shipment.id}>
                  {shipment.carrier ? <p>{shipment.carrier}</p> : null}
                  {shipment.tracking_number ? (
                    <p className="font-mono text-xs text-muted-foreground">
                      {shipment.tracking_number}
                    </p>
                  ) : null}
                </div>
              ))}
            </div>
          ) : null}
        </AdminCard>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <AdminCard title="Line items" className="lg:col-span-2" contentClassName="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product</TableHead>
                <TableHead className="hidden sm:table-cell">SKU</TableHead>
                <TableHead className="text-right">Qty</TableHead>
                <TableHead className="text-right">Unit (ex GST)</TableHead>
                <TableHead className="text-right">GST</TableHead>
                <TableHead className="text-right">Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {order.items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <div className="font-medium">{item.product_name}</div>
                    {item.variant_name ? (
                      <div className="text-sm text-muted-foreground">{item.variant_name}</div>
                    ) : null}
                  </TableCell>
                  <TableCell className="hidden font-mono text-sm text-muted-foreground sm:table-cell">
                    {item.sku}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">{item.quantity}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatAud(item.unit_price_ex_gst_cents)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatAud(item.unit_gst_cents * item.quantity)}
                  </TableCell>
                  <TableCell className="text-right font-medium tabular-nums">
                    {formatAud(item.line_total_inc_gst_cents)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </AdminCard>

        <AdminCard title="Order summary">
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Subtotal (ex GST)</dt>
              <dd className="tabular-nums">{formatAud(order.totals.subtotal_ex_gst_cents)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">GST</dt>
              <dd className="tabular-nums">{formatAud(order.totals.gst_total_cents)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">Shipping (inc GST)</dt>
              <dd className="tabular-nums">{formatAud(shippingIncGst)}</dd>
            </div>
            {order.totals.discount_cents > 0 ? (
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Discount</dt>
                <dd className="tabular-nums">-{formatAud(order.totals.discount_cents)}</dd>
              </div>
            ) : null}
            <div className="flex justify-between border-t border-border pt-2 font-semibold">
              <dt>Total (inc GST)</dt>
              <dd className="tabular-nums">{formatAud(order.totals.total_inc_gst_cents)}</dd>
            </div>
          </dl>
        </AdminCard>
      </div>

      <AdminCard title="Status timeline" description="Fulfilment progress for this order">
        <OrderTimeline order={order} />
      </AdminCard>

      {order.customer_notes ? (
        <AdminCard title="Customer notes">
          <p className="text-sm text-muted-foreground">{order.customer_notes}</p>
        </AdminCard>
      ) : null}
    </div>
  );
}

export { OrderDetailPageView };
