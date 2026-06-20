import type { Metadata } from "next";

import { CrmOpportunitiesPageView } from "@/components/admin/pages/crm-opportunities-page-view";

export const metadata: Metadata = { title: "CRM Opportunities | Admin | A2Z Tools" };

export default function AdminCrmOpportunitiesPage() {
  return <CrmOpportunitiesPageView />;
}
