"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";

import {
  addToCart,
  applyCartCoupon,
  clearCart,
  fetchCart,
  mergeGuestCart,
  removeCartCoupon,
  removeCartItem,
  updateCartItem,
} from "../services/cart.service";
import type {
  AddToCartPayload,
  ApplyCouponPayload,
  Cart,
  MergeCartPayload,
  UpdateCartItemPayload,
} from "../types/cart";
import { queryKeys } from "./query-keys";

export function useCart(
  options?: Omit<UseQueryOptions<Cart, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.cart.current(),
    queryFn: fetchCart,
    staleTime: 0,
    ...options,
  });
}

export function useAddToCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: AddToCartPayload) => addToCart(payload),
    onSuccess: (cart) => {
      queryClient.setQueryData(queryKeys.cart.current(), cart);
    },
  });
}

export function useUpdateCartItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      itemId,
      payload,
    }: {
      itemId: string;
      payload: UpdateCartItemPayload;
    }) => updateCartItem(itemId, payload),
    onSuccess: (cart) => {
      queryClient.setQueryData(queryKeys.cart.current(), cart);
    },
  });
}

export function useRemoveCartItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId: string) => removeCartItem(itemId),
    onSuccess: (cart) => {
      queryClient.setQueryData(queryKeys.cart.current(), cart);
    },
  });
}

export function useClearCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: clearCart,
    onSuccess: (cart) => {
      queryClient.setQueryData(queryKeys.cart.current(), cart);
    },
  });
}

export function useApplyCartCoupon() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ApplyCouponPayload) => applyCartCoupon(payload),
    onSuccess: (cart) => {
      queryClient.setQueryData(queryKeys.cart.current(), cart);
    },
  });
}

export function useRemoveCartCoupon() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: removeCartCoupon,
    onSuccess: (cart) => {
      queryClient.setQueryData(queryKeys.cart.current(), cart);
    },
  });
}

export function useMergeGuestCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: MergeCartPayload) => mergeGuestCart(payload),
    onSuccess: (cart) => {
      queryClient.setQueryData(queryKeys.cart.current(), cart);
    },
  });
}
