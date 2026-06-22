import type { Metadata } from "next";

import { OrderDetailPageView } from "@/components/admin/pages/order-detail-page-view";

export const metadata: Metadata = { title: "Order | Admin | A2Z Tools" };

export default async function AdminOrderDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <OrderDetailPageView orderId={id} />;
}
