import type { Metadata } from "next";

import { PurchaseRequestsListPageView } from "@/components/admin/pages/purchase-requests-list-page-view";

export const metadata: Metadata = { title: "Requisitions | Procurement | A2Z Tools" };

export default function PurchaseRequestsListPage() {
  return <PurchaseRequestsListPageView />;
}
