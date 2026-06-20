"use client";

import { useWishlist } from "@/components/wishlist/wishlist-provider";
import { WishlistItemCard } from "@/components/wishlist/wishlist-item-card";
import { cn } from "@/lib/utils";

export interface WishlistGridProps {
  className?: string;
}

function WishlistGrid({ className }: WishlistGridProps) {
  const { items } = useWishlist();

  return (
    <ul
      className={cn(
        "grid gap-5 sm:grid-cols-2 xl:grid-cols-3",
        className
      )}
    >
      {items.map((item) => (
        <li key={item.id}>
          <WishlistItemCard item={item} />
        </li>
      ))}
    </ul>
  );
}

export { WishlistGrid };
