import type { Metadata } from "next";

import { SupplierPortalPoDetailView } from "@/components/supplier-portal/supplier-portal-po-detail-view";

export const metadata: Metadata = { title: "Purchase Order | Supplier Portal | A2Z Tools" };

export default async function SupplierPortalPoDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <SupplierPortalPoDetailView poId={id} />;
}
