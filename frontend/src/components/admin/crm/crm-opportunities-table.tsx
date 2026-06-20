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
import type { CrmOpportunity } from "@/lib/api/admin/types";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(cents / 100);
}

export interface CrmOpportunitiesTableProps {
  opportunities: CrmOpportunity[];
}

function CrmOpportunitiesTable({ opportunities }: CrmOpportunitiesTableProps) {
  if (opportunities.length === 0) {
    return <p className="text-sm text-muted-foreground">No opportunities yet.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Opportunity</TableHead>
          <TableHead>Account</TableHead>
          <TableHead>Stage</TableHead>
          <TableHead className="text-right">Expected</TableHead>
          <TableHead className="text-right">Probability</TableHead>
          <TableHead className="text-right">Weighted</TableHead>
          <TableHead>Close date</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {opportunities.map((opp) => (
          <TableRow key={opp.id}>
            <TableCell className="font-medium">
              <Link
                href={`/admin-dashboard/crm/opportunities/${opp.id}`}
                className="hover:underline"
              >
                {opp.name}
              </Link>
            </TableCell>
            <TableCell>{opp.partyName}</TableCell>
            <TableCell>
              <Badge variant="secondary" className="capitalize">
                {opp.stage.replace("_", " ")}
              </Badge>
            </TableCell>
            <TableCell className="text-right tabular-nums">
              {formatAud(opp.expectedRevenueCents)}
            </TableCell>
            <TableCell className="text-right tabular-nums">{opp.probability}%</TableCell>
            <TableCell className="text-right tabular-nums">
              {formatAud(opp.weightedRevenueCents)}
            </TableCell>
            <TableCell>{opp.expectedCloseDate ?? "—"}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { CrmOpportunitiesTable };
