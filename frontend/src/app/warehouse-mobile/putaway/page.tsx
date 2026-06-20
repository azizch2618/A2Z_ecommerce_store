import type { Metadata } from "next";

import { WarehouseMobilePutawayView } from "@/components/warehouse-mobile/warehouse-mobile-views";

export const metadata: Metadata = { title: "Putaway | Warehouse Floor | A2Z Tools" };

export default function WarehouseMobilePutawayPage() {
  return <WarehouseMobilePutawayView />;
}
