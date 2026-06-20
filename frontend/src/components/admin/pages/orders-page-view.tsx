"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { RecentOrdersTable } from "@/components/admin/dashboard/recent-orders-table";
import { useAdminOrders } from "@/lib/api/admin/hooks";

function OrdersPageView() {
  const { data, isLoading, isError } = useAdminOrders();

  return (
    <AdminListPage
      title="Orders"
      description="Manage customer orders from pending through delivery."
      isLoading={isLoading}
      isError={isError}
    >
      <AdminCard title="All orders" description="Filter by status, date, or customer" contentClassName="p-0">
        <RecentOrdersTable orders={data ?? []} />
      </AdminCard>
    </AdminListPage>
  );
}

export { OrdersPageView };
