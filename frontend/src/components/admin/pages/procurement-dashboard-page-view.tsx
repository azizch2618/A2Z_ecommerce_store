"use client";

import Link from "next/link";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { ProcurementKpiGrid } from "@/components/admin/procurement/procurement-kpi-grid";
import { PurchaseRequestsTable } from "@/components/admin/procurement/purchase-requests-table";
import { Button } from "@/components/ui/button";
import {
  useProcurementDashboard,
  usePurchaseRequests,
} from "@/lib/api/admin/procurement-hooks";

function ProcurementDashboardPageView() {
  const dashboard = useProcurementDashboard();
  const requests = usePurchaseRequests();

  return (
    <AdminListPage
      title="Procurement"
      description="Purchase requisitions, supplier performance, and procurement spend."
      isLoading={dashboard.isLoading || requests.isLoading}
      isError={dashboard.isError || requests.isError}
      actions={
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/procurement/requisitions">All requisitions</Link>
        </Button>
      }
    >
      {dashboard.data ? <ProcurementKpiGrid kpis={dashboard.data} /> : null}

      <AdminCard title="Recent requisitions">
        <PurchaseRequestsTable requests={(requests.data ?? []).slice(0, 10)} />
      </AdminCard>
    </AdminListPage>
  );
}

export { ProcurementDashboardPageView };
