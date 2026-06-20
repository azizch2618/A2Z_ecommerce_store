"use client";

import Link from "next/link";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { CrmDashboardChartsPanel } from "@/components/admin/crm/crm-dashboard-charts";
import { CrmKpiGrid } from "@/components/admin/crm/crm-kpi-grid";
import { CrmLeadsTable } from "@/components/admin/crm/crm-leads-table";
import { CrmOpportunitiesTable } from "@/components/admin/crm/crm-opportunities-table";
import { Button } from "@/components/ui/button";
import { useCrmDashboard, useCrmLeads, useCrmOpportunities } from "@/lib/api/admin/crm-hooks";

function CrmDashboardPageView() {
  const dashboard = useCrmDashboard();
  const leads = useCrmLeads();
  const opportunities = useCrmOpportunities({ status: "open" });

  const isLoading = dashboard.isLoading || leads.isLoading || opportunities.isLoading;
  const isError = dashboard.isError || leads.isError || opportunities.isError;

  return (
    <AdminListPage
      title="CRM"
      description="Leads, opportunities, and sales pipeline on the ERP Party model."
      isLoading={isLoading}
      isError={isError}
      actions={
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" asChild>
            <Link href="/admin-dashboard/crm/pipeline">Pipeline</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/admin-dashboard/crm/leads">Leads</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/admin-dashboard/crm/opportunities">Opportunities</Link>
          </Button>
        </div>
      }
    >
      {dashboard.data ? <CrmKpiGrid kpis={dashboard.data} /> : null}

      {dashboard.data?.charts ? (
        <CrmDashboardChartsPanel charts={dashboard.data.charts} />
      ) : null}

      <div className="grid gap-6 xl:grid-cols-2">
        <AdminCard title="Recent leads">
          <CrmLeadsTable leads={(leads.data ?? []).slice(0, 8)} />
        </AdminCard>
        <AdminCard title="Open opportunities">
          <CrmOpportunitiesTable opportunities={(opportunities.data ?? []).slice(0, 8)} />
        </AdminCard>
      </div>
    </AdminListPage>
  );
}

export { CrmDashboardPageView };
