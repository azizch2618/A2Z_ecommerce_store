"use client";

import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { PurchaseRequestsTable } from "@/components/admin/procurement/purchase-requests-table";
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
  useApprovePurchaseRequest,
  useConvertPurchaseRequest,
  usePurchaseRequestDetail,
  useRejectPurchaseRequest,
  useSubmitPurchaseRequest,
} from "@/lib/api/admin/procurement-hooks";
import { useHasPermission } from "@/hooks/use-permissions";
import { Permission } from "@/lib/rbac";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

export interface PurchaseRequestDetailPageViewProps {
  requestId: string;
}

function PurchaseRequestDetailPageView({ requestId }: PurchaseRequestDetailPageViewProps) {
  const { data: request, isLoading, isError } = usePurchaseRequestDetail(requestId);
  const submit = useSubmitPurchaseRequest();
  const approve = useApprovePurchaseRequest();
  const reject = useRejectPurchaseRequest();
  const convert = useConvertPurchaseRequest();
  const canApprove = useHasPermission(Permission.PROCUREMENT_APPROVE);
  const isPending =
    submit.isPending || approve.isPending || reject.isPending || convert.isPending;

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !request) {
    return (
      <div className="space-y-4">
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/procurement/requisitions">
            <ArrowLeft className="mr-2 size-4" />
            Back to requisitions
          </Link>
        </Button>
        <p className="text-muted-foreground">Purchase requisition not found.</p>
      </div>
    );
  }

  const lineTotal = request.lines.reduce(
    (sum, line) => sum + line.quantity * line.unitCostCents,
    0
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Button variant="ghost" size="sm" asChild className="mb-2 -ml-2">
            <Link href="/admin-dashboard/procurement/requisitions">
              <ArrowLeft className="mr-1 size-4" />
              Requisitions
            </Link>
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">{request.requestNumber}</h1>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge className="capitalize">{request.status}</Badge>
            <Badge variant="secondary" className="capitalize">
              {request.priority} priority
            </Badge>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {request.status === "draft" ? (
            <Button onClick={() => void submit.mutateAsync(requestId)} disabled={isPending}>
              Submit
            </Button>
          ) : null}
          {request.status === "submitted" && canApprove ? (
            <>
              <Button
                variant="outline"
                onClick={() => void reject.mutateAsync({ id: requestId })}
                disabled={isPending}
              >
                Reject
              </Button>
              <Button
                onClick={() => void approve.mutateAsync({ id: requestId })}
                disabled={isPending}
              >
                Approve
              </Button>
            </>
          ) : null}
          {request.status === "approved" ? (
            <Button onClick={() => void convert.mutateAsync(requestId)} disabled={isPending}>
              Convert to PO
            </Button>
          ) : null}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <AdminCard title="Request details" className="lg:col-span-1">
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-muted-foreground">Requested by</dt>
              <dd className="font-medium">{request.requestedBy?.email ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Department</dt>
              <dd className="font-medium">{request.departmentName ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Cost center</dt>
              <dd className="font-medium">{request.costCenterName ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Warehouse</dt>
              <dd className="font-medium">{request.warehouseCode ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Supplier</dt>
              <dd className="font-medium">{request.supplierName ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Est. value (ex GST)</dt>
              <dd className="font-medium">{formatAud(lineTotal)}</dd>
            </div>
            {request.convertedPoNumber ? (
              <div>
                <dt className="text-muted-foreground">Purchase order</dt>
                <dd className="font-medium">{request.convertedPoNumber}</dd>
              </div>
            ) : null}
          </dl>
        </AdminCard>

        <AdminCard title="Justification" className="lg:col-span-2">
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">
            {request.justification || "No justification provided."}
          </p>
        </AdminCard>
      </div>

      <AdminCard title="Line items">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>SKU</TableHead>
              <TableHead>Product</TableHead>
              <TableHead className="text-right">Qty</TableHead>
              <TableHead className="text-right">Unit cost</TableHead>
              <TableHead className="text-right">Line total</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {request.lines.map((line) => (
              <TableRow key={line.id}>
                <TableCell className="font-medium">{line.sku}</TableCell>
                <TableCell>{line.productName}</TableCell>
                <TableCell className="text-right">{line.quantity}</TableCell>
                <TableCell className="text-right">{formatAud(line.unitCostCents)}</TableCell>
                <TableCell className="text-right">
                  {formatAud(line.quantity * line.unitCostCents)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </AdminCard>
    </div>
  );
}

export { PurchaseRequestDetailPageView };
