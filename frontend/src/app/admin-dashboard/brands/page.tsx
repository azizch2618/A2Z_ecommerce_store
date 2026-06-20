import type { Metadata } from "next";

import { BrandsPageView } from "@/components/admin/pages/brands-page-view";

export const metadata: Metadata = { title: "Brands | Admin | A2Z Tools" };

export default function AdminBrandsPage() {
  return <BrandsPageView />;
}
