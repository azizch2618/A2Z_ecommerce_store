import type { Metadata } from "next";

import { PickDetailMobile } from "@/components/warehouse-mobile/warehouse-mobile-views";

export const metadata: Metadata = { title: "Pick Detail | Warehouse Floor | A2Z Tools" };

export default async function WarehouseMobilePickDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="mx-auto min-h-screen max-w-lg p-4">
      <PickDetailMobile pickId={id} />
    </div>
  );
}
