import type { Metadata } from "next";

import { CustomerDetailPageView } from "@/components/admin/pages/customer-detail-page-view";

export const metadata: Metadata = { title: "Customer | Admin | A2Z Tools" };

export default async function AdminCustomerDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <CustomerDetailPageView customerId={id} />;
}
