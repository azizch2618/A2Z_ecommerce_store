"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";

import { getAccountBreadcrumbs } from "@/config/account";
import { mapApiOrderToAccountOrder } from "@/lib/api/mappers/account-mapper";
import { useOrders } from "@/lib/api/hooks/use-orders";
import { AccountOrdersTable, AccountShell } from "@/components/account";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";

function AccountOrdersPageView() {
  const { data, isLoading, isError } = useOrders({ limit: 50 });

  const orders = React.useMemo(
    () => (data?.data ?? []).map(mapApiOrderToAccountOrder),
    [data]
  );

  return (
    <>
      <PageBreadcrumbs items={getAccountBreadcrumbs("Orders")} />
      <AccountShell title="Orders" description="View and track your order history.">
        {isLoading ? (
          <div className="flex min-h-[30vh] items-center justify-center">
            <Loader2 className="size-8 animate-spin text-brand-blue" />
          </div>
        ) : isError ? (
          <p className="text-sm text-muted-foreground">Could not load orders.</p>
        ) : (
          <AccountOrdersTable orders={orders} />
        )}
      </AccountShell>
    </>
  );
}

export { AccountOrdersPageView };
