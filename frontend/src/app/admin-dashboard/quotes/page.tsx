import type { Metadata } from "next";

import { QuotesDashboardPageView } from "@/components/admin/pages/quotes-dashboard-page-view";

export const metadata: Metadata = { title: "Quotes | Admin | A2Z Tools" };

export default function AdminQuotesPage() {
  return <QuotesDashboardPageView />;
}
