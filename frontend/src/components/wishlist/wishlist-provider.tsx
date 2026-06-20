"use client";

import * as React from "react";
import { toast } from "sonner";

import type { ProductDetail } from "@/config/product-detail";
import { hasAuthTokens } from "@/lib/api/auth/token-storage";
import { mapApiWishlistItemToUi } from "@/lib/api/mappers/wishlist-mapper";
import {
  useAddToWishlist,
  useRemoveWishlistItem,
  useWishlistQuery,
} from "@/lib/api/hooks/use-wishlist";
import { useAddToCart } from "@/lib/api/hooks/use-cart";
import type { ListingProduct } from "@/types/product";
import type { WishlistItem } from "@/types/wishlist";

interface WishlistContextValue {
  items: WishlistItem[];
  count: number;
  isWishlisted: (productId: string) => boolean;
  addItem: (item: WishlistItem) => void;
  removeItem: (id: string) => void;
  toggleFromListing: (product: ListingProduct) => void;
  toggleFromDetail: (product: ProductDetail) => void;
  moveToCart: (id: string) => void;
  isLoading: boolean;
}

const WishlistContext = React.createContext<WishlistContextValue | null>(null);

function WishlistProvider({ children }: { children: React.ReactNode }) {
  const authed = hasAuthTokens();
  const { data: wishlist, isLoading } = useWishlistQuery({ enabled: authed });
  const addMutation = useAddToWishlist();
  const removeMutation = useRemoveWishlistItem();
  const addToCartMutation = useAddToCart();

  const items = React.useMemo(
    () => (wishlist?.items ?? []).map(mapApiWishlistItemToUi),
    [wishlist]
  );

  const isWishlisted = React.useCallback(
    (productId: string) => items.some((item) => item.productId === productId),
    [items]
  );

  const addItem = React.useCallback((item: WishlistItem) => {
    if (!authed) {
      toast.info("Sign in to save items to your wishlist");
      return;
    }
    if (!item.variantId) return;
    addMutation.mutate({ variant_id: item.variantId });
  }, [addMutation, authed]);

  const removeItem = React.useCallback(
    (id: string) => {
      if (!authed) return;
      const item = items.find((entry) => entry.id === id || entry.productId === id);
      if (!item) return;
      removeMutation.mutate(item.id);
    },
    [authed, items, removeMutation]
  );

  const toggleFromListing = React.useCallback(
    (product: ListingProduct) => {
      if (!authed) {
        toast.info("Sign in to save items to your wishlist");
        return;
      }
      const existing = items.find((item) => item.productId === product.id);
      if (existing) {
        removeMutation.mutate(existing.id);
        toast.info(`${product.name} removed from wishlist`);
        return;
      }
      if (!product.defaultVariantId) {
        toast.error("Could not add item — missing variant");
        return;
      }
      addMutation.mutate(
        { variant_id: product.defaultVariantId },
        {
          onSuccess: () => toast.success(`${product.name} added to wishlist`),
        }
      );
    },
    [addMutation, authed, items, removeMutation]
  );

  const toggleFromDetail = React.useCallback(
    (product: ProductDetail) => {
      if (!authed) {
        toast.info("Sign in to save items to your wishlist");
        return;
      }
      const existing = items.find((item) => item.productId === product.id);
      if (existing) {
        removeMutation.mutate(existing.id);
        toast.info(`${product.name} removed from wishlist`);
        return;
      }
      if (!product.defaultVariantId) {
        toast.error("Could not add item — missing variant");
        return;
      }
      addMutation.mutate(
        { variant_id: product.defaultVariantId },
        {
          onSuccess: () => toast.success(`${product.name} added to wishlist`),
        }
      );
    },
    [addMutation, authed, items, removeMutation]
  );

  const moveToCart = React.useCallback(
    async (id: string) => {
      const item = items.find((entry) => entry.id === id || entry.productId === id);
      if (!item) return;

      if (item.stock === "out_of_stock") {
        toast.error("This item is out of stock");
        return;
      }

      if (!item.variantId) {
        toast.error("Could not move item to cart");
        return;
      }

      try {
        await addToCartMutation.mutateAsync({
          variant_id: item.variantId,
          quantity: 1,
        });
        await removeMutation.mutateAsync(item.id);
        toast.success(`${item.name} moved to cart`);
      } catch {
        toast.error("Could not move item to cart");
      }
    },
    [addToCartMutation, items, removeMutation]
  );

  const value = React.useMemo(
    () => ({
      items,
      count: items.length,
      isWishlisted,
      addItem,
      removeItem,
      toggleFromListing,
      toggleFromDetail,
      moveToCart,
      isLoading,
    }),
    [
      items,
      isWishlisted,
      addItem,
      removeItem,
      toggleFromListing,
      toggleFromDetail,
      moveToCart,
      isLoading,
    ]
  );

  return (
    <WishlistContext.Provider value={value}>{children}</WishlistContext.Provider>
  );
}

function useWishlist() {
  const context = React.useContext(WishlistContext);
  if (!context) {
    throw new Error("useWishlist must be used within WishlistProvider");
  }
  return context;
}

export { WishlistProvider, useWishlist };
