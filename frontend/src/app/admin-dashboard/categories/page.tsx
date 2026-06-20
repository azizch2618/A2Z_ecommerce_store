import type { Metadata } from "next";

import { CategoriesPageView } from "@/components/admin/pages/categories-page-view";

export const metadata: Metadata = { title: "Categories | Admin | A2Z Tools" };

export default function AdminCategoriesPage() {
  return <CategoriesPageView />;
}
