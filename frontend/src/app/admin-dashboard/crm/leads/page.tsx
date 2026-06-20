import type { Metadata } from "next";

import { CrmLeadsPageView } from "@/components/admin/pages/crm-leads-page-view";

export const metadata: Metadata = { title: "CRM Leads | Admin | A2Z Tools" };

export default function AdminCrmLeadsPage() {
  return <CrmLeadsPageView />;
}
