import type { Metadata } from "next";

import { SupplierPortalPoListView } from "@/components/supplier-portal/supplier-portal-po-list-view";

export const metadata: Metadata = { title: "Purchase Orders | Supplier Portal | A2Z Tools" };

export default function SupplierPortalPoListPage() {
  return <SupplierPortalPoListView />;
}
