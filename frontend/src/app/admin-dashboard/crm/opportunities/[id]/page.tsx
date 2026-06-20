import type { Metadata } from "next";

import { CrmOpportunityDetailPageView } from "@/components/admin/pages/crm-opportunity-detail-page-view";

export const metadata: Metadata = { title: "Opportunity Detail | CRM | A2Z Tools" };

export default async function AdminCrmOpportunityDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <CrmOpportunityDetailPageView opportunityId={id} />;
}
