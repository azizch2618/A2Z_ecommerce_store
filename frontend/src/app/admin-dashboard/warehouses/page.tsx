import type { Metadata } from "next";

import { WarehousesPageView } from "@/components/admin/pages/warehouses-page-view";

export const metadata: Metadata = { title: "Warehouses | Admin | A2Z Tools" };

export default function AdminWarehousesPage() {
  return <WarehousesPageView />;
}
