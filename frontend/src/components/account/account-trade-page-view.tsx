"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import type { SavedQuote } from "@/types/account";
import { getAccountBreadcrumbs } from "@/config/account";
import { useTradeAccount, useQuotes } from "@/lib/api/hooks/use-trade-account";
import { acceptCustomerQuote, rejectCustomerQuote } from "@/lib/api/admin/quotes-service";
import { queryKeys } from "@/lib/api/hooks/query-keys";
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
  const queryClient = useQueryClient();
  const [pendingQuoteId, setPendingQuoteId] = React.useState<string | null>(null);
  const { data: tradeAccount, isLoading: tradeLoading } = useTradeAccount();
  const { data: quotesData, isLoading: quotesLoading } = useQuotes({ limit: 20 });

  const acceptQuote = useMutation({
    mutationFn: acceptCustomerQuote,
    onMutate: (id) => setPendingQuoteId(id),
    onSettled: () => {
      setPendingQuoteId(null);
      void queryClient.invalidateQueries({ queryKey: queryKeys.tradeAccounts.quotes() });
    },
  });

  const rejectQuote = useMutation({
    mutationFn: (id: string) => rejectCustomerQuote(id),
    onMutate: (id) => setPendingQuoteId(id),
    onSettled: () => {
      setPendingQuoteId(null);
      void queryClient.invalidateQueries({ queryKey: queryKeys.tradeAccounts.quotes() });
    },
  });

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
          onAcceptQuote={(id) => void acceptQuote.mutate(id)}
          onRejectQuote={(id) => void rejectQuote.mutate(id)}
          quoteActionPendingId={pendingQuoteId}
        />
      </AccountShell>
    </>
  );
}

export { AccountTradePageView };
