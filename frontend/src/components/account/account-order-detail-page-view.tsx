"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";

import { getAccountBreadcrumbs } from "@/config/account";
import { mapApiOrderToAccountOrder } from "@/lib/api/mappers/account-mapper";
import { useOrder } from "@/lib/api/hooks/use-orders";
import { formatAud } from "@/lib/cart";
import { AccountShell } from "@/components/account/account-shell";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
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
import { cn } from "@/lib/utils";

const statusStyles = {
  processing: "bg-warning-light text-warning dark:bg-warning-light/20",
  shipped: "bg-brand-blue-light text-brand-blue dark:bg-brand-blue-light/15",
  delivered: "bg-success-light text-success dark:bg-success-light/20",
  cancelled: "bg-error-light text-error dark:bg-error-light/20",
} as const;

function formatOrderDate(iso: string) {
  return new Intl.DateTimeFormat("en-AU", {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
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

export interface AccountOrderDetailPageViewProps {
  orderId: string;
}

function AccountOrderDetailPageView({ orderId }: AccountOrderDetailPageViewProps) {
  const { data: order, isLoading, isError } = useOrder(orderId);

  const accountOrder = React.useMemo(
    () => (order ? mapApiOrderToAccountOrder(order) : null),
    [order]
  );

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-brand-blue" />
      </div>
    );
  }

  if (isError || !order || !accountOrder) {
    return (
      <>
        <PageBreadcrumbs items={getAccountBreadcrumbs("Orders")} />
        <AccountShell title="Order not found" description="This order could not be loaded.">
          <Button asChild variant="outline">
            <Link href="/account/orders">
              <ArrowLeft className="mr-2 size-4" />
              Back to orders
            </Link>
          </Button>
        </AccountShell>
      </>
    );
  }

  return (
    <>
      <PageBreadcrumbs
        items={[
          ...getAccountBreadcrumbs("Orders").slice(0, -1),
          { label: "Orders", href: "/account/orders" },
          { label: accountOrder.orderNumber, href: `/account/orders/${orderId}` },
        ]}
      />
      <AccountShell
        title={`Order ${accountOrder.orderNumber}`}
        description={`Placed ${formatOrderDate(accountOrder.date)}`}
      >
        <div className="space-y-6">
          <div className="flex flex-wrap items-center gap-3">
            <Badge
              variant="outline"
              className={cn("border-0 capitalize", statusStyles[accountOrder.status])}
            >
              {accountOrder.status}
            </Badge>
            <span className="text-sm text-muted-foreground">
              Payment: {order.payment_status.replace("_", " ")}
            </span>
          </div>

          <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Product</TableHead>
                  <TableHead className="hidden sm:table-cell">SKU</TableHead>
                  <TableHead className="text-right">Qty</TableHead>
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
                    <TableCell className="text-right font-medium tabular-nums">
                      {formatAud(item.line_total_inc_gst_cents / 100)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
              <h2 className="text-sm font-semibold text-foreground">Shipping address</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                {formatAddress(order.shipping_address)}
              </p>
            </div>
            <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
              <h2 className="text-sm font-semibold text-foreground">Order summary</h2>
              <dl className="mt-3 space-y-2 text-sm">
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Subtotal (ex GST)</dt>
                  <dd className="tabular-nums">
                    {formatAud(order.totals.subtotal_ex_gst_cents / 100)}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">GST</dt>
                  <dd className="tabular-nums">
                    {formatAud(order.totals.gst_total_cents / 100)}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Shipping</dt>
                  <dd className="tabular-nums">
                    {formatAud(
                      (order.totals.shipping_ex_gst_cents + order.totals.shipping_gst_cents) /
                        100
                    )}
                  </dd>
                </div>
                <div className="flex justify-between border-t border-border pt-2 font-semibold">
                  <dt>Total (inc GST)</dt>
                  <dd className="tabular-nums">
                    {formatAud(order.totals.total_inc_gst_cents / 100)}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          <Button asChild variant="outline">
            <Link href="/account/orders">
              <ArrowLeft className="mr-2 size-4" />
              Back to orders
            </Link>
          </Button>
        </div>
      </AccountShell>
    </>
  );
}

export { AccountOrderDetailPageView };
