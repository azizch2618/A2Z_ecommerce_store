import type { Metadata } from "next";

import { OrdersPageView } from "@/components/admin/pages/orders-page-view";

export const metadata: Metadata = { title: "Orders | Admin | A2Z Tools" };

export default function AdminOrdersPage() {
  return <OrdersPageView />;
}
