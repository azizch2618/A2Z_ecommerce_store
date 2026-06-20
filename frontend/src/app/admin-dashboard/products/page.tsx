import type { Metadata } from "next";

import { ProductsPageView } from "@/components/admin/pages/products-page-view";

export const metadata: Metadata = { title: "Products | Admin | A2Z Tools" };

export default function AdminProductsPage() {
  return <ProductsPageView />;
}
