"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { RecentCustomersTable } from "@/components/admin/dashboard/recent-customers-table";
import { useAdminCustomers } from "@/lib/api/admin/hooks";

function CustomersPageView() {
  const { data, isLoading, isError } = useAdminCustomers();

  return (
    <AdminListPage
      title="Customers"
      description="Retail and trade customer accounts."
      isLoading={isLoading}
      isError={isError}
    >
      <AdminCard title="Customer directory" contentClassName="p-0">
        <RecentCustomersTable customers={data ?? []} />
      </AdminCard>
    </AdminListPage>
  );
}

export { CustomersPageView };
