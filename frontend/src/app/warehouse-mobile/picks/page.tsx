import type { Metadata } from "next";

import { WarehouseMobilePicksView } from "@/components/warehouse-mobile/warehouse-mobile-views";

export const metadata: Metadata = { title: "Pick | Warehouse Floor | A2Z Tools" };

export default function WarehouseMobilePicksPage() {
  return <WarehouseMobilePicksView />;
}
