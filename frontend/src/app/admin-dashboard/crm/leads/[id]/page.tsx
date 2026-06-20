import type { Metadata } from "next";

import { CrmLeadDetailPageView } from "@/components/admin/pages/crm-lead-detail-page-view";

export const metadata: Metadata = { title: "Lead Detail | CRM | A2Z Tools" };

export default async function AdminCrmLeadDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <CrmLeadDetailPageView leadId={id} />;
}
