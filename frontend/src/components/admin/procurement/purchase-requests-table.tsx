"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { PurchaseRequest } from "@/lib/api/admin/procurement-types";

const statusVariant: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
  draft: "secondary",
  submitted: "outline",
  approved: "default",
  rejected: "destructive",
  converted: "secondary",
};

export interface PurchaseRequestsTableProps {
  requests: PurchaseRequest[];
  showLinks?: boolean;
}

function PurchaseRequestsTable({ requests, showLinks = true }: PurchaseRequestsTableProps) {
  if (requests.length === 0) {
    return <p className="text-sm text-muted-foreground">No purchase requisitions found.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Request #</TableHead>
          <TableHead>Priority</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Supplier</TableHead>
          <TableHead>Requested by</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {requests.map((request) => (
          <TableRow key={request.id}>
            <TableCell className="font-medium">
              {showLinks ? (
                <Link
                  href={`/admin-dashboard/procurement/requisitions/${request.id}`}
                  className="hover:underline"
                >
                  {request.requestNumber}
                </Link>
              ) : (
                request.requestNumber
              )}
            </TableCell>
            <TableCell className="capitalize">{request.priority}</TableCell>
            <TableCell>
              <Badge variant={statusVariant[request.status] ?? "secondary"} className="capitalize">
                {request.status}
              </Badge>
            </TableCell>
            <TableCell>{request.supplierName ?? "—"}</TableCell>
            <TableCell>{request.requestedBy?.email ?? "—"}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { PurchaseRequestsTable };
