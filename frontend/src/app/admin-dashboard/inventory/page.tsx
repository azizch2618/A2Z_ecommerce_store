import type { Metadata } from "next";

import { InventoryWmsView } from "@/components/admin/inventory/inventory-wms-view";

export const metadata: Metadata = { title: "Inventory | Admin | A2Z Tools" };

export default function AdminInventoryPage() {
  return <InventoryWmsView />;
}
