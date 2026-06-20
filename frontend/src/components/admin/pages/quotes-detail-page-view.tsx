"use client";

import Link from "next/link";
import { ArrowLeft, Download, Loader2 } from "lucide-react";

import { AdminCard } from "@/components/admin/shared/admin-card";
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
  useApproveQuote,
  useConvertQuote,
  useQuoteDetail,
  useRejectQuote,
  useSendQuote,
  useSubmitQuote,
} from "@/lib/api/admin/quotes-hooks";
import { quotePdfUrl } from "@/lib/api/admin/quotes-service";
import { useHasPermission } from "@/hooks/use-permissions";
import { Permission } from "@/lib/rbac";

function formatAud(cents: number): string {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

export interface QuotesDetailPageViewProps {
  quoteId: string;
}

function QuotesDetailPageView({ quoteId }: QuotesDetailPageViewProps) {
  const { data: quote, isLoading, isError } = useQuoteDetail(quoteId);
  const submit = useSubmitQuote();
  const approve = useApproveQuote();
  const reject = useRejectQuote();
  const send = useSendQuote();
  const convert = useConvertQuote();
  const canApprove = useHasPermission(Permission.QUOTES_APPROVE);
  const isPending =
    submit.isPending ||
    approve.isPending ||
    reject.isPending ||
    send.isPending ||
    convert.isPending;

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !quote) {
    return (
      <div className="space-y-4">
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/quotes">
            <ArrowLeft className="mr-2 size-4" />
            Back to quotes
          </Link>
        </Button>
        <p className="text-muted-foreground">Quote not found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Button variant="ghost" size="sm" asChild className="mb-2 -ml-2">
            <Link href="/admin-dashboard/quotes">
              <ArrowLeft className="mr-1 size-4" />
              Quotes
            </Link>
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">{quote.quoteNumber}</h1>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge className="capitalize">{quote.status.replace(/_/g, " ")}</Badge>
            {quote.partyName ? <Badge variant="secondary">{quote.partyName}</Badge> : null}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" asChild>
            <a href={quotePdfUrl(quoteId)} target="_blank" rel="noopener noreferrer">
              <Download className="mr-2 size-4" />
              PDF
            </a>
          </Button>
          {quote.status === "draft" ? (
            <Button onClick={() => void submit.mutateAsync(quoteId)} disabled={isPending}>
              Submit
            </Button>
          ) : null}
          {quote.status === "pending_approval" && canApprove ? (
            <>
              <Button
                variant="outline"
                onClick={() => void reject.mutateAsync({ id: quoteId })}
                disabled={isPending}
              >
                Reject
              </Button>
              <Button onClick={() => void approve.mutateAsync({ id: quoteId })} disabled={isPending}>
                Approve
              </Button>
            </>
          ) : null}
          {quote.status === "approved" || quote.status === "draft" ? (
            <Button onClick={() => void send.mutateAsync(quoteId)} disabled={isPending}>
              Send to customer
            </Button>
          ) : null}
          {quote.status === "accepted" ? (
            <Button onClick={() => void convert.mutateAsync(quoteId)} disabled={isPending}>
              Convert to order
            </Button>
          ) : null}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <AdminCard title="Summary" className="lg:col-span-1">
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-muted-foreground">Valid until</dt>
              <dd className="font-medium">
                {quote.validUntil
                  ? new Date(quote.validUntil).toLocaleDateString("en-AU")
                  : "—"}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Subtotal (ex GST)</dt>
              <dd className="font-medium">{formatAud(quote.subtotalExGstCents)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">GST</dt>
              <dd className="font-medium">{formatAud(quote.gstTotalCents)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Total (inc GST)</dt>
              <dd className="text-lg font-semibold">{formatAud(quote.totalIncGstCents)}</dd>
            </div>
            {quote.convertedOrderNumber ? (
              <div>
                <dt className="text-muted-foreground">Sales order</dt>
                <dd className="font-medium">{quote.convertedOrderNumber}</dd>
              </div>
            ) : null}
            {quote.opportunityId ? (
              <div>
                <dt className="text-muted-foreground">Opportunity</dt>
                <dd>
                  <Link
                    href={`/admin-dashboard/crm/opportunities/${quote.opportunityId}`}
                    className="font-medium text-primary hover:underline"
                  >
                    View opportunity
                  </Link>
                </dd>
              </div>
            ) : null}
          </dl>
        </AdminCard>

        <AdminCard title="Line items" className="lg:col-span-2">
          {quote.lines.length === 0 ? (
            <p className="text-sm text-muted-foreground">No line items yet.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>SKU</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead className="text-right">Qty</TableHead>
                  <TableHead className="text-right">Unit</TableHead>
                  <TableHead className="text-right">Total</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {quote.lines.map((line) => (
                  <TableRow key={line.id}>
                    <TableCell>{line.sku}</TableCell>
                    <TableCell>{line.productName}</TableCell>
                    <TableCell className="text-right">{line.quantity}</TableCell>
                    <TableCell className="text-right">
                      {formatAud(line.unitPriceExGstCents)}
                    </TableCell>
                    <TableCell className="text-right">
                      {formatAud(line.lineTotalIncGstCents)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </AdminCard>
      </div>

      {quote.notes ? (
        <AdminCard title="Notes">
          <p className="whitespace-pre-wrap text-sm">{quote.notes}</p>
        </AdminCard>
      ) : null}

      {quote.termsAndConditions ? (
        <AdminCard title="Terms & conditions">
          <p className="whitespace-pre-wrap text-sm text-muted-foreground">
            {quote.termsAndConditions}
          </p>
        </AdminCard>
      ) : null}
    </div>
  );
}

export { QuotesDetailPageView };
