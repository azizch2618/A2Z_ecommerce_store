"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { Loader2 } from "lucide-react";

import { wishlistBreadcrumbs } from "@/config/wishlist";
import { hasAuthTokens } from "@/lib/api/auth/token-storage";
import { useWishlist } from "@/components/wishlist/wishlist-provider";
import { WishlistEmptyState } from "@/components/wishlist/wishlist-empty-state";
import { WishlistGrid } from "@/components/wishlist/wishlist-grid";
import { WishlistShareButton } from "@/components/wishlist/wishlist-share-button";
import { Container } from "@/components/layout/container";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

function WishlistPageView() {
  const { items, count, isLoading } = useWishlist();
  const authed = hasAuthTokens();

  if (!authed) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-brand-blue" />
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <>
        <PageBreadcrumbs items={wishlistBreadcrumbs} />
        <WishlistEmptyState />
      </>
    );
  }

  return (
    <>
      <PageBreadcrumbs items={wishlistBreadcrumbs} />

      <Container className="py-8 md:py-10">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-bold text-foreground md:text-3xl">
                Wishlist
              </h1>
              <Badge
                variant="secondary"
                className="bg-brand-blue-light font-semibold text-brand-navy dark:text-foreground"
              >
                {count} {count === 1 ? "item" : "items"}
              </Badge>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Saved products with trade pricing and stock status — move items to cart
              when ready.
            </p>
          </div>

          <div className="flex flex-wrap gap-2 self-start sm:self-auto">
            <WishlistShareButton />
            <Button asChild variant="outline" className="gap-2">
              <Link href="/products">
                <ArrowLeft className="size-4" />
                Continue shopping
              </Link>
            </Button>
          </div>
        </div>

        <WishlistGrid />
      </Container>
    </>
  );
}

export { WishlistPageView };
