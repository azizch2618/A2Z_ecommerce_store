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
import { useSupplierPortalPos } from "@/lib/api/admin/procurement-hooks";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

function SupplierPortalPoListView() {
  const pos = useSupplierPortalPos();

  if (pos.isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <Button variant="ghost" size="sm" asChild className="-ml-2 mb-2">
            <Link href="/supplier-portal">← Supplier portal</Link>
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">Purchase orders</h1>
        </div>
      </div>

      {(pos.data ?? []).length === 0 ? (
        <p className="text-sm text-muted-foreground">No purchase orders assigned.</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>PO #</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Expected</TableHead>
              <TableHead className="text-right">Total</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {(pos.data ?? []).map((po) => (
              <TableRow key={po.id}>
                <TableCell>
                  <Link
                    href={`/supplier-portal/purchase-orders/${po.id}`}
                    className="font-medium hover:underline"
                  >
                    {po.poNumber}
                  </Link>
                </TableCell>
                <TableCell>
                  <Badge className="capitalize">{po.status.replace(/_/g, " ")}</Badge>
                </TableCell>
                <TableCell>
                  {po.expectedAt
                    ? new Date(po.expectedAt).toLocaleDateString("en-AU")
                    : "—"}
                </TableCell>
                <TableCell className="text-right">{formatAud(po.totalExGstCents)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}

export { SupplierPortalPoListView };
