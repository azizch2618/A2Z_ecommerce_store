import type { Metadata } from "next";

import { WarehouseMobileHomeView } from "@/components/warehouse-mobile/warehouse-mobile-views";

export const metadata: Metadata = { title: "Warehouse Floor | A2Z Tools" };

export default function WarehouseMobilePage() {
  return <WarehouseMobileHomeView />;
}
