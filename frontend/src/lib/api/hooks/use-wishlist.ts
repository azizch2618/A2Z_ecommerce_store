"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";

import { hasAuthTokens } from "../auth/token-storage";
import {
  addToWishlist,
  fetchWishlist,
  removeWishlistItem,
} from "../services/wishlist.service";
import type { AddToWishlistPayload, Wishlist } from "../types/wishlist";
import { queryKeys } from "./query-keys";

export function useWishlistQuery(
  options?: Omit<UseQueryOptions<Wishlist, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.wishlist.current(),
    queryFn: fetchWishlist,
    enabled: hasAuthTokens(),
    staleTime: 30_000,
    ...options,
  });
}

export function useAddToWishlist() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AddToWishlistPayload) => addToWishlist(payload),
    onSuccess: (wishlist) => {
      queryClient.setQueryData(queryKeys.wishlist.current(), wishlist);
    },
  });
}

export function useRemoveWishlistItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId: string) => removeWishlistItem(itemId),
    onSuccess: (wishlist) => {
      queryClient.setQueryData(queryKeys.wishlist.current(), wishlist);
    },
  });
}
