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
import type { PayrollPeriod } from "@/lib/api/admin/payroll-types";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

const statusVariant: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
  draft: "secondary",
  calculated: "outline",
  approved: "default",
  posted: "default",
};

export interface PayrollPeriodsTableProps {
  periods: PayrollPeriod[];
}

function PayrollPeriodsTable({ periods }: PayrollPeriodsTableProps) {
  if (periods.length === 0) {
    return <p className="text-sm text-muted-foreground">No payroll periods found.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Run #</TableHead>
          <TableHead>Name</TableHead>
          <TableHead>Pay date</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Net pay</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {periods.map((period) => (
          <TableRow key={period.id}>
            <TableCell className="font-medium">{period.periodNumber}</TableCell>
            <TableCell>{period.name}</TableCell>
            <TableCell>{period.payDate}</TableCell>
            <TableCell>
              <Badge variant={statusVariant[period.status] ?? "secondary"} className="capitalize">
                {period.status}
              </Badge>
            </TableCell>
            <TableCell className="text-right">
              {period.totalNetCents > 0 ? formatAud(period.totalNetCents) : "—"}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { PayrollPeriodsTable };
