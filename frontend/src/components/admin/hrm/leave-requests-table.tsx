"use client";

import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { LeaveRequest } from "@/lib/api/admin/hrm-types";

const statusVariant: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
  draft: "secondary",
  submitted: "outline",
  approved: "default",
  rejected: "destructive",
};

export interface LeaveRequestsTableProps {
  requests: LeaveRequest[];
}

function LeaveRequestsTable({ requests }: LeaveRequestsTableProps) {
  if (requests.length === 0) {
    return <p className="text-sm text-muted-foreground">No leave requests found.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Request #</TableHead>
          <TableHead>Employee</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Dates</TableHead>
          <TableHead>Days</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {requests.map((request) => (
          <TableRow key={request.id}>
            <TableCell className="font-medium">{request.requestNumber}</TableCell>
            <TableCell>{request.employeeName}</TableCell>
            <TableCell className="capitalize">{request.leaveType.replace("_", " ")}</TableCell>
            <TableCell>
              {request.startDate} → {request.endDate}
            </TableCell>
            <TableCell>{request.days}</TableCell>
            <TableCell>
              <Badge variant={statusVariant[request.status] ?? "secondary"} className="capitalize">
                {request.status}
              </Badge>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { LeaveRequestsTable };
