"use client";

import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";

import { CrmTimelineFeed } from "@/components/admin/crm/crm-timeline-feed";
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
import { useAdminCustomerDetail } from "@/lib/api/admin/hooks";

function formatAud(cents: number) {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

function formatDate(value: string | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en-AU", { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(value)
  );
}

export interface CustomerDetailPageViewProps {
  customerId: string;
}

function CustomerDetailPageView({ customerId }: CustomerDetailPageViewProps) {
  const { data, isLoading, isError } = useAdminCustomerDetail(customerId);

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="space-y-4">
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/customers">
            <ArrowLeft className="mr-2 size-4" />
            Back to customers
          </Link>
        </Button>
        <p className="text-muted-foreground">Customer not found.</p>
      </div>
    );
  }

  const { profile, lifetimeValue, tradeAccount, orders, quotes, crmActivities } = data;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Button variant="ghost" size="sm" asChild className="mb-2 -ml-2">
            <Link href="/admin-dashboard/customers">
              <ArrowLeft className="mr-1 size-4" />
              Customers
            </Link>
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">{profile.name}</h1>
          <p className="mt-1 text-muted-foreground">{profile.email || "No email on file"}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge variant="secondary" className="capitalize">
              {profile.customerType}
            </Badge>
            {profile.tradeStatus ? (
              <Badge
                variant={
                  profile.tradeStatus === "approved"
                    ? "success"
                    : profile.tradeStatus === "pending"
                      ? "warning"
                      : "destructive"
                }
                className="capitalize"
              >
                Trade {profile.tradeStatus}
              </Badge>
            ) : null}
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <AdminCard title="Lifetime value" description="Paid order revenue">
          <p className="text-2xl font-semibold tabular-nums">{formatAud(lifetimeValue.totalSpentCents)}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            {lifetimeValue.orderCount} orders · avg {formatAud(lifetimeValue.averageOrderCents)}
          </p>
        </AdminCard>
        <AdminCard title="Quotes" description="Sales pipeline">
          <p className="text-2xl font-semibold tabular-nums">{lifetimeValue.quoteCount}</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Accepted/sent value {formatAud(lifetimeValue.acceptedQuoteValueCents)}
          </p>
        </AdminCard>
        <AdminCard title="Member since">
          <p className="text-lg font-medium">{formatDate(profile.joinedAt)}</p>
          {profile.phone ? (
            <p className="mt-1 text-sm text-muted-foreground">{profile.phone}</p>
          ) : null}
        </AdminCard>
        <AdminCard title="Trade account" description="B2B credit status">
          {tradeAccount ? (
            <>
              <p className="text-lg font-medium capitalize">{tradeAccount.status ?? "—"}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {tradeAccount.accountNumber ? `#${tradeAccount.accountNumber}` : "No account number"}
              </p>
              <p className="mt-1 text-sm tabular-nums">
                Credit {formatAud(tradeAccount.creditAvailableCents)} /{" "}
                {formatAud(tradeAccount.creditLimitCents)}
              </p>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Retail customer — no trade account</p>
          )}
        </AdminCard>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <AdminCard title="Profile">
          <dl className="grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-muted-foreground">Customer type</dt>
              <dd className="font-medium capitalize">{profile.customerType}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Email</dt>
              <dd className="font-medium">{profile.email || "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Phone</dt>
              <dd className="font-medium">{profile.phone || "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Joined</dt>
              <dd className="font-medium">{formatDate(profile.joinedAt)}</dd>
            </div>
            {profile.organization ? (
              <>
                <div className="sm:col-span-2">
                  <dt className="text-muted-foreground">Organization</dt>
                  <dd className="font-medium">{profile.organization.tradingName}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Legal name</dt>
                  <dd className="font-medium">{profile.organization.legalName}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">ABN</dt>
                  <dd className="font-medium">{profile.organization.abn || "—"}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Segment</dt>
                  <dd className="font-medium capitalize">{profile.organization.segment}</dd>
                </div>
              </>
            ) : null}
          </dl>
        </AdminCard>

        <AdminCard title="CRM activities" description="Calls, notes, and timeline">
          <CrmTimelineFeed entries={crmActivities} />
        </AdminCard>
      </div>

      <AdminCard title="Orders" description={`${orders.length} recent orders`} contentClassName="p-0">
        {orders.length ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Payment</TableHead>
                <TableHead className="text-right">Items</TableHead>
                <TableHead className="text-right">Total</TableHead>
                <TableHead>Placed</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {orders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell className="font-mono text-xs">{order.orderNumber}</TableCell>
                  <TableCell className="capitalize">{order.status.replace(/_/g, " ")}</TableCell>
                  <TableCell className="capitalize">{order.paymentStatus}</TableCell>
                  <TableCell className="text-right tabular-nums">{order.itemCount}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatAud(order.totalIncGstCents)}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatDate(order.placedAt)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <p className="p-4 text-sm text-muted-foreground">No orders yet.</p>
        )}
      </AdminCard>

      <AdminCard title="Quotes" description={`${quotes.length} recent quotes`} contentClassName="p-0">
        {quotes.length ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Quote</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Total (inc GST)</TableHead>
                <TableHead>Valid until</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {quotes.map((quote) => (
                <TableRow key={quote.id}>
                  <TableCell className="font-mono text-xs">{quote.quoteNumber}</TableCell>
                  <TableCell>
                    <Badge variant="secondary" className="capitalize">
                      {quote.status.replace(/_/g, " ")}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatAud(quote.totalIncGstCents)}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatDate(quote.validUntil)}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button size="sm" variant="outline" asChild>
                      <Link href={`/admin-dashboard/quotes/${quote.id}`}>View</Link>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <p className="p-4 text-sm text-muted-foreground">No quotes yet.</p>
        )}
      </AdminCard>
    </div>
  );
}

export { CustomerDetailPageView };
