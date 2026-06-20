"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";

import { getAccountBreadcrumbs } from "@/config/account";
import { mapApiAddressToSavedAddress } from "@/lib/api/mappers/account-mapper";
import { useAddresses } from "@/lib/api/hooks/use-auth";
import { AccountAddressesList, AccountShell } from "@/components/account";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";

function AccountAddressesPageView() {
  const { data, isLoading, isError } = useAddresses();

  const addresses = React.useMemo(
    () => (data?.data ?? []).map(mapApiAddressToSavedAddress),
    [data]
  );

  return (
    <>
      <PageBreadcrumbs items={getAccountBreadcrumbs("Saved Addresses")} />
      <AccountShell title="Saved addresses" description="Manage delivery and billing addresses.">
        {isLoading ? (
          <div className="flex min-h-[30vh] items-center justify-center">
            <Loader2 className="size-8 animate-spin text-brand-blue" />
          </div>
        ) : isError ? (
          <p className="text-sm text-muted-foreground">Could not load addresses.</p>
        ) : (
          <AccountAddressesList addresses={addresses} />
        )}
      </AccountShell>
    </>
  );
}

export { AccountAddressesPageView };
