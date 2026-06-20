"use client";

import Link from "next/link";
import { Loader2 } from "lucide-react";

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
import {
  useSupplierPortalDashboard,
  useSupplierPortalPos,
} from "@/lib/api/admin/procurement-hooks";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

function SupplierPortalDashboardView() {
  const dashboard = useSupplierPortalDashboard();
  const pos = useSupplierPortalPos();

  if (dashboard.isLoading || pos.isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const kpis = dashboard.data;

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Supplier Portal</h1>
          <p className="text-sm text-muted-foreground">
            View purchase orders, acknowledge deliveries, and track payments.
          </p>
        </div>
        <Button variant="outline" asChild>
          <Link href="/supplier-portal/purchase-orders">All purchase orders</Link>
        </Button>
      </div>

      {kpis ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            { label: "Open POs", value: String(kpis.openPurchaseOrders ?? 0) },
            { label: "On-time delivery", value: `${kpis.onTimeDeliveryPct.toFixed(1)}%` },
            { label: "Avg lead time", value: `${kpis.avgLeadTimeDays.toFixed(1)} days` },
            { label: "Spend", value: formatAud(kpis.purchaseSpendCents) },
          ].map((item) => (
            <div key={item.label} className="rounded-lg border bg-card p-4">
              <p className="text-sm text-muted-foreground">{item.label}</p>
              <p className="mt-1 text-2xl font-bold">{item.value}</p>
            </div>
          ))}
        </div>
      ) : null}

      <div className="rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <h2 className="font-semibold">Recent purchase orders</h2>
        </div>
        {(pos.data ?? []).length === 0 ? (
          <p className="p-4 text-sm text-muted-foreground">No purchase orders yet.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>PO #</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(pos.data ?? []).slice(0, 8).map((po) => (
                <TableRow key={po.id}>
                  <TableCell>
                    <Link href={`/supplier-portal/purchase-orders/${po.id}`} className="font-medium hover:underline">
                      {po.poNumber}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Badge className="capitalize">{po.status.replace(/_/g, " ")}</Badge>
                  </TableCell>
                  <TableCell className="text-right">{formatAud(po.totalExGstCents)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}

export { SupplierPortalDashboardView };
