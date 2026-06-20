import type { Metadata } from "next";

import { QuotesListPageView } from "@/components/admin/pages/quotes-list-page-view";

export const metadata: Metadata = { title: "All Quotes | Admin | A2Z Tools" };

export default function AdminQuotesListPage() {
  return <QuotesListPageView />;
}
