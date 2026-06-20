import type { Metadata } from "next";

import { QuotesDetailPageView } from "@/components/admin/pages/quotes-detail-page-view";

export const metadata: Metadata = { title: "Quote Detail | Admin | A2Z Tools" };

export default async function AdminQuoteDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <QuotesDetailPageView quoteId={id} />;
}
