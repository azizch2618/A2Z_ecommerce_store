import type { Metadata } from "next";

import { CrmPipelinePageView } from "@/components/admin/pages/crm-pipeline-page-view";

export const metadata: Metadata = { title: "CRM Pipeline | Admin | A2Z Tools" };

export default function AdminCrmPipelinePage() {
  return <CrmPipelinePageView />;
}
