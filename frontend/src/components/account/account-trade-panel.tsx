import Link from "next/link";
import { BadgePercent, Building2, CreditCard, FileText } from "lucide-react";

import type { SavedQuote } from "@/types/account";
import { formatAud } from "@/lib/cart";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const quoteStatusStyles = {
  draft: "bg-muted text-muted-foreground",
  sent: "bg-brand-blue-light text-brand-blue dark:bg-brand-blue-light/15",
  accepted: "bg-success-light text-success dark:bg-success-light/20",
  expired: "bg-error-light text-error dark:bg-error-light/20",
} as const;

export interface AccountTradePanelProps {
  quotes: SavedQuote[];
  companyName: string;
  abn: string;
  tradeStatus: "approved" | "pending" | "suspended" | "rejected";
  creditLimit: number;
  paymentTermsDays: number | null;
  onAcceptQuote?: (quoteId: string) => void;
  onRejectQuote?: (quoteId: string) => void;
  quoteActionPendingId?: string | null;
}

function AccountTradePanel({
  quotes,
  companyName,
  abn,
  tradeStatus,
  creditLimit,
  paymentTermsDays,
  onAcceptQuote,
  onRejectQuote,
  quoteActionPendingId,
}: AccountTradePanelProps) {
  const isApproved = tradeStatus === "approved";

  return (
    <div className="space-y-6">
      <Card className="overflow-hidden border-brand-blue/20">
        <CardHeader className="bg-brand-blue-light/30 dark:bg-brand-blue-light/10">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="flex size-10 items-center justify-center rounded-lg bg-brand-blue text-white">
                <Building2 className="size-5" aria-hidden />
              </span>
              <div>
                <CardTitle className="text-lg">Trade account</CardTitle>
                <CardDescription>{companyName}</CardDescription>
              </div>
            </div>
            <Badge
              className={cn(
                isApproved
                  ? "bg-success text-white hover:bg-success"
                  : "bg-warning text-white hover:bg-warning"
              )}
            >
              {isApproved ? "Approved" : "Pending review"}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="grid gap-4 pt-6 sm:grid-cols-3">
          <div>
            <p className="text-xs text-muted-foreground">ABN</p>
            <p className="mt-1 font-mono text-sm font-medium">{abn || "—"}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Credit limit</p>
            <p className="mt-1 text-sm font-semibold tabular-nums">
              {creditLimit ? formatAud(creditLimit) : "—"}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Payment terms</p>
            <p className="mt-1 text-sm font-medium">
              {paymentTermsDays ? `Net ${paymentTermsDays}` : "—"}
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-3">
        {[
          { icon: BadgePercent, label: "Trade pricing", detail: "Applied at checkout" },
          { icon: CreditCard, label: "Net 30 terms", detail: "On approved orders" },
          { icon: FileText, label: "Tax invoices", detail: "ABN & GST on every order" },
        ].map(({ icon: Icon, label, detail }) => (
          <div
            key={label}
            className="flex items-start gap-3 rounded-xl border border-border bg-card p-4 shadow-sm"
          >
            <Icon className="mt-0.5 size-5 shrink-0 text-brand-blue" aria-hidden />
            <div>
              <p className="text-sm font-semibold text-foreground">{label}</p>
              <p className="text-xs text-muted-foreground">{detail}</p>
            </div>
          </div>
        ))}
      </div>

      <div>
        <div className="mb-4 flex items-center justify-between gap-4">
          <h3 className="text-lg font-semibold text-foreground">Saved quotes</h3>
          <Button asChild variant="outline" size="sm">
            <Link href="/trade/quote">Request quote</Link>
          </Button>
        </div>
        <ul className="space-y-3">
          {quotes.map((quote) => (
            <li
              key={quote.id}
              className="flex flex-col gap-3 rounded-xl border border-border bg-card p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between"
            >
              <div className="min-w-0">
                <p className="font-mono text-xs text-muted-foreground">
                  {quote.quoteNumber}
                </p>
                <p className="mt-0.5 font-medium text-foreground">{quote.title}</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Expires{" "}
                  {new Intl.DateTimeFormat("en-AU", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                  }).format(new Date(quote.expiresAt))}
                </p>
              </div>
              <div className="flex flex-col items-stretch gap-2 sm:items-end">
                <Badge
                  variant="outline"
                  className={cn("border-0 capitalize", quoteStatusStyles[quote.status as keyof typeof quoteStatusStyles] ?? quoteStatusStyles.draft)}
                >
                  {quote.status.replace(/_/g, " ")}
                </Badge>
                <p className="font-semibold tabular-nums text-foreground">
                  {formatAud(quote.totalIncGst)}
                </p>
                {quote.status === "sent" && onAcceptQuote && onRejectQuote ? (
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      disabled={quoteActionPendingId === quote.id}
                      onClick={() => onRejectQuote(quote.id)}
                    >
                      Decline
                    </Button>
                    <Button
                      size="sm"
                      disabled={quoteActionPendingId === quote.id}
                      onClick={() => onAcceptQuote(quote.id)}
                    >
                      Accept
                    </Button>
                  </div>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export { AccountTradePanel };
