"use client";

import Link from "next/link";

import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { PurchaseRequestsTable } from "@/components/admin/procurement/purchase-requests-table";
import { Button } from "@/components/ui/button";
import { usePurchaseRequests } from "@/lib/api/admin/procurement-hooks";

function PurchaseRequestsListPageView() {
  const requests = usePurchaseRequests();

  return (
    <AdminListPage
      title="Purchase requisitions"
      description="Draft, submit, approve, and convert requisitions to purchase orders."
      isLoading={requests.isLoading}
      isError={requests.isError}
      actions={
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/procurement">Dashboard</Link>
        </Button>
      }
    >
      <PurchaseRequestsTable requests={requests.data ?? []} />
    </AdminListPage>
  );
}

export { PurchaseRequestsListPageView };
