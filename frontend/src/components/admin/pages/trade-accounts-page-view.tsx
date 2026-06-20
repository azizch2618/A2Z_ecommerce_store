"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { TradeApplicationsPanel } from "@/components/admin/dashboard/trade-applications-panel";
import { useAdminTradeApplications } from "@/lib/api/admin/hooks";

function TradeAccountsPageView() {
  const { data, isLoading, isError } = useAdminTradeApplications();

  return (
    <AdminListPage
      title="Trade accounts"
      description="Review applications and manage trade customer pricing."
      isLoading={isLoading}
      isError={isError}
    >
      <AdminCard title="Trade applications">
        <TradeApplicationsPanel applications={data ?? []} />
      </AdminCard>
    </AdminListPage>
  );
}

export { TradeAccountsPageView };
