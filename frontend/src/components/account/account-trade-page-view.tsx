"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";

import type { SavedQuote } from "@/types/account";
import { getAccountBreadcrumbs } from "@/config/account";
import { useTradeAccount, useQuotes } from "@/lib/api/hooks/use-trade-account";
import { AccountShell, AccountTradePanel } from "@/components/account";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";

function mapQuote(quote: {
  id: string;
  quote_number: string;
  created_at: string;
  total_inc_gst_cents: number;
  status: string;
  valid_until: string;
}): SavedQuote {
  return {
    id: quote.id,
    quoteNumber: quote.quote_number,
    title: `Quote ${quote.quote_number}`,
    date: quote.created_at,
    totalIncGst: quote.total_inc_gst_cents / 100,
    status: quote.status as SavedQuote["status"],
    expiresAt: quote.valid_until,
  };
}

function AccountTradePageView() {
  const { data: tradeAccount, isLoading: tradeLoading } = useTradeAccount();
  const { data: quotesData, isLoading: quotesLoading } = useQuotes({ limit: 20 });

  if (tradeLoading || quotesLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-brand-blue" />
      </div>
    );
  }

  const quotes = (quotesData?.data ?? []).map(mapQuote);

  return (
    <>
      <PageBreadcrumbs items={getAccountBreadcrumbs("Trade Account")} />
      <AccountShell title="Trade account" description="Manage trade pricing, credit, and project quotes.">
        <AccountTradePanel
          quotes={quotes}
          companyName={
            tradeAccount?.organization.trading_name ??
            tradeAccount?.organization.legal_name ??
            ""
          }
          abn={tradeAccount?.organization.abn ?? ""}
          tradeStatus={tradeAccount?.status ?? "pending"}
          creditLimit={tradeAccount ? tradeAccount.credit_limit_cents / 100 : 0}
          paymentTermsDays={tradeAccount?.payment_terms_days ?? null}
        />
      </AccountShell>
    </>
  );
}

export { AccountTradePageView };
