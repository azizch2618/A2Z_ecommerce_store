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
import type { Quote } from "@/lib/api/admin/quotes-types";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

const statusVariant: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
  draft: "secondary",
  pending_approval: "outline",
  approved: "default",
  rejected: "destructive",
  sent: "default",
  accepted: "default",
  expired: "destructive",
  converted: "secondary",
};

export interface QuotesTableProps {
  quotes: Quote[];
  showLinks?: boolean;
}

function QuotesTable({ quotes, showLinks = true }: QuotesTableProps) {
  if (quotes.length === 0) {
    return <p className="text-sm text-muted-foreground">No quotes found.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Quote #</TableHead>
          <TableHead>Customer</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Total</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {quotes.map((quote) => (
          <TableRow key={quote.id}>
            <TableCell className="font-medium">
              {showLinks ? (
                <Link
                  href={`/admin-dashboard/quotes/${quote.id}`}
                  className="hover:underline"
                >
                  {quote.quoteNumber}
                </Link>
              ) : (
                quote.quoteNumber
              )}
            </TableCell>
            <TableCell>{quote.partyName ?? "—"}</TableCell>
            <TableCell>
              <Badge variant={statusVariant[quote.status] ?? "secondary"} className="capitalize">
                {quote.status.replace(/_/g, " ")}
              </Badge>
            </TableCell>
            <TableCell className="text-right">{formatAud(quote.totalIncGstCents)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { QuotesTable };
