"use client";

import Link from "next/link";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { QuotesKpiGrid } from "@/components/admin/quotes/quotes-kpi-grid";
import { QuotesTable } from "@/components/admin/quotes/quotes-table";
import { Button } from "@/components/ui/button";
import { useQuotes, useQuotesDashboard } from "@/lib/api/admin/quotes-hooks";

function QuotesDashboardPageView() {
  const dashboard = useQuotesDashboard();
  const quotes = useQuotes();

  return (
    <AdminListPage
      title="Quotations"
      description="Quote lifecycle, approval workflow, and conversion to sales orders."
      isLoading={dashboard.isLoading || quotes.isLoading}
      isError={dashboard.isError || quotes.isError}
      actions={
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/quotes/list">All quotes</Link>
        </Button>
      }
    >
      {dashboard.data ? <QuotesKpiGrid kpis={dashboard.data} /> : null}

      <AdminCard title="Recent quotes">
        <QuotesTable quotes={(quotes.data ?? []).slice(0, 10)} />
      </AdminCard>
    </AdminListPage>
  );
}

export { QuotesDashboardPageView };
