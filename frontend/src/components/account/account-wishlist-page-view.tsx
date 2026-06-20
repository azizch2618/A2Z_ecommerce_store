"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowRight, Loader2 } from "lucide-react";

import { getAccountBreadcrumbs } from "@/config/account";
import { AccountShell, AccountWishlistSection } from "@/components/account";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
import { Button } from "@/components/ui/button";
import { useWishlist } from "@/components/wishlist/wishlist-provider";

function AccountWishlistPageView() {
  const { isLoading } = useWishlist();

  return (
    <>
      <PageBreadcrumbs items={getAccountBreadcrumbs("Wishlist")} />
      <AccountShell
        title="Wishlist"
        description="Saved products with trade pricing where available."
      >
        {isLoading ? (
          <div className="flex min-h-[30vh] items-center justify-center">
            <Loader2 className="size-8 animate-spin text-brand-blue" />
          </div>
        ) : (
          <>
            <AccountWishlistSection />
            <div className="mt-6 flex justify-end">
              <Button asChild variant="outline" size="sm" className="gap-2">
                <Link href="/wishlist">
                  Open full wishlist
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
            </div>
          </>
        )}
      </AccountShell>
    </>
  );
}

export { AccountWishlistPageView };
