"use client";

import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { useWishlist } from "@/components/wishlist/wishlist-provider";
import { WishlistEmptyState } from "@/components/wishlist/wishlist-empty-state";
import { WishlistGrid } from "@/components/wishlist/wishlist-grid";
import { Button } from "@/components/ui/button";

export interface AccountWishlistSectionProps {
  className?: string;
}

function AccountWishlistSection({ className }: AccountWishlistSectionProps) {
  const { items } = useWishlist();

  if (items.length === 0) {
    return <WishlistEmptyState />;
  }

  return (
    <div className={className}>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">
          {items.length} saved {items.length === 1 ? "product" : "products"}
        </p>
        <Button asChild variant="outline" size="sm" className="gap-2">
          <Link href="/wishlist">
            Open full wishlist
            <ArrowRight className="size-4" />
          </Link>
        </Button>
      </div>
      <WishlistGrid />
    </div>
  );
}

export { AccountWishlistSection };
