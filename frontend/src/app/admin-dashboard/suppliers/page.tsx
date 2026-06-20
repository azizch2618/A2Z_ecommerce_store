import type { Metadata } from "next";

import { SuppliersPageView } from "@/components/admin/pages/suppliers-page-view";

export const metadata: Metadata = { title: "Suppliers | Admin | A2Z Tools" };

export default function AdminSuppliersPage() {
  return <SuppliersPageView />;
}
