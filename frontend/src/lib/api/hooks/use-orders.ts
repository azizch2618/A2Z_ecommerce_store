"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";

import { hasAuthTokens } from "../auth/token-storage";
import {
  cancelOrder,
  createOrder,
  fetchOrderById,
  fetchOrders,
  reorder,
} from "../services/orders.service";
import type {
  CreateOrderPayload,
  OrderDetail,
  OrderListParams,
  OrderListResponse,
} from "../types/order";
import { queryKeys } from "./query-keys";

export function useOrders(
  params?: OrderListParams,
  options?: Omit<
    UseQueryOptions<OrderListResponse, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: queryKeys.orders.list(params),
    queryFn: () => fetchOrders(params),
    enabled: hasAuthTokens(),
    staleTime: 30_000,
    ...options,
  });
}

export function useOrder(
  orderId: string,
  options?: Omit<UseQueryOptions<OrderDetail, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.orders.detail(orderId),
    queryFn: () => fetchOrderById(orderId),
    enabled: Boolean(orderId),
    ...options,
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateOrderPayload) => createOrder(payload),
    onSuccess: (order) => {
      queryClient.setQueryData(queryKeys.orders.detail(order.id), order);
      void queryClient.invalidateQueries({ queryKey: queryKeys.orders.lists() });
      void queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}

export function useCancelOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderId: string) => cancelOrder(orderId),
    onSuccess: (order) => {
      queryClient.setQueryData(queryKeys.orders.detail(order.id), order);
      void queryClient.invalidateQueries({ queryKey: queryKeys.orders.lists() });
    },
  });
}

export function useReorder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderId: string) => reorder(orderId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}
