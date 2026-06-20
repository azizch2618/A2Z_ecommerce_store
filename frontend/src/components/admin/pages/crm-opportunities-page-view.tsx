"use client";

import Link from "next/link";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { CrmOpportunitiesTable } from "@/components/admin/crm/crm-opportunities-table";
import { Button } from "@/components/ui/button";
import { useCrmOpportunities } from "@/lib/api/admin/crm-hooks";

function CrmOpportunitiesPageView() {
  const { data, isLoading, isError } = useCrmOpportunities();

  return (
    <AdminListPage
      title="Opportunities"
      description="Pipeline linked to leads, customers, and trade accounts via Party."
      isLoading={isLoading}
      isError={isError}
      actions={
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/crm">CRM dashboard</Link>
        </Button>
      }
    >
      <AdminCard title="Pipeline">
        <CrmOpportunitiesTable opportunities={data ?? []} />
      </AdminCard>
    </AdminListPage>
  );
}

export { CrmOpportunitiesPageView };
