import type { Metadata } from "next";

import { PurchaseRequestDetailPageView } from "@/components/admin/pages/purchase-request-detail-page-view";

export const metadata: Metadata = { title: "Requisition | Procurement | A2Z Tools" };

export default async function PurchaseRequestDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <PurchaseRequestDetailPageView requestId={id} />;
}
