import type { Metadata } from "next";

import { CustomersPageView } from "@/components/admin/pages/customers-page-view";

export const metadata: Metadata = { title: "Customers | Admin | A2Z Tools" };

export default function AdminCustomersPage() {
  return <CustomersPageView />;
}
