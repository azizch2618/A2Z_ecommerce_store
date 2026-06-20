"use client";

import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";
import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  useAcknowledgeSupplierPo,
  useSupplierPoPaymentStatus,
  useSupplierPortalPoDetail,
  useUpdateSupplierPoExpectedDelivery,
} from "@/lib/api/admin/procurement-hooks";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

export interface SupplierPortalPoDetailViewProps {
  poId: string;
}

function SupplierPortalPoDetailView({ poId }: SupplierPortalPoDetailViewProps) {
  const { data: po, isLoading, isError } = useSupplierPortalPoDetail(poId);
  const payment = useSupplierPoPaymentStatus(poId);
  const acknowledge = useAcknowledgeSupplierPo();
  const updateDelivery = useUpdateSupplierPoExpectedDelivery();
  const [expectedAt, setExpectedAt] = useState("");

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !po) {
    return (
      <div className="mx-auto max-w-4xl space-y-4 p-6">
        <Button variant="outline" asChild>
          <Link href="/supplier-portal/purchase-orders">
            <ArrowLeft className="mr-2 size-4" />
            Back
          </Link>
        </Button>
        <p className="text-muted-foreground">Purchase order not found.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-6">
      <Button variant="ghost" size="sm" asChild className="-ml-2">
        <Link href="/supplier-portal/purchase-orders">
          <ArrowLeft className="mr-1 size-4" />
          Purchase orders
        </Link>
      </Button>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{po.poNumber}</h1>
          <Badge className="mt-2 capitalize">{po.status.replace(/_/g, " ")}</Badge>
        </div>
        <div className="flex flex-wrap gap-2">
          {!po.acknowledgedAt ? (
            <Button
              onClick={() => void acknowledge.mutateAsync(poId)}
              disabled={acknowledge.isPending}
            >
              Acknowledge PO
            </Button>
          ) : null}
        </div>
      </div>

      <div className="grid gap-4 rounded-lg border bg-card p-4 sm:grid-cols-2">
        <div>
          <p className="text-sm text-muted-foreground">Total (ex GST)</p>
          <p className="font-semibold">{formatAud(po.totalExGstCents)}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Warehouse</p>
          <p className="font-semibold">{po.warehouseCode}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Expected delivery</p>
          <p className="font-semibold">
            {po.expectedAt ? new Date(po.expectedAt).toLocaleDateString("en-AU") : "Not set"}
          </p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Acknowledged</p>
          <p className="font-semibold">
            {po.acknowledgedAt
              ? new Date(po.acknowledgedAt).toLocaleString("en-AU")
              : "Pending"}
          </p>
        </div>
        {payment.data ? (
          <>
            <div>
              <p className="text-sm text-muted-foreground">Payment status</p>
              <p className="font-semibold capitalize">
                {payment.data.paymentStatus.replace(/_/g, " ")}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Payment terms</p>
              <p className="font-semibold">{payment.data.termsDays} days</p>
            </div>
          </>
        ) : null}
      </div>

      <div className="rounded-lg border bg-card p-4 space-y-3">
        <h2 className="font-semibold">Update expected delivery</h2>
        <div className="flex flex-wrap gap-2">
          <Input
            type="datetime-local"
            value={expectedAt}
            onChange={(e) => setExpectedAt(e.target.value)}
            className="max-w-xs"
          />
          <Button
            variant="outline"
            disabled={!expectedAt || updateDelivery.isPending}
            onClick={() =>
              void updateDelivery.mutateAsync({
                id: poId,
                expectedAt: new Date(expectedAt).toISOString(),
              })
            }
          >
            Save date
          </Button>
        </div>
      </div>

      <div className="rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <h2 className="font-semibold">Line items</h2>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>SKU</TableHead>
              <TableHead>Product</TableHead>
              <TableHead className="text-right">Ordered</TableHead>
              <TableHead className="text-right">Received</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {po.lines.map((line) => (
              <TableRow key={line.id}>
                <TableCell className="font-medium">{line.sku}</TableCell>
                <TableCell>{line.productName}</TableCell>
                <TableCell className="text-right">{line.quantityOrdered}</TableCell>
                <TableCell className="text-right">{line.quantityReceived}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

export { SupplierPortalPoDetailView };
