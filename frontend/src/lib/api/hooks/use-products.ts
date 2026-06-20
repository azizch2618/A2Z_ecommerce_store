"use client";

import {
  useInfiniteQuery,
  useQuery,
  type UseInfiniteQueryOptions,
  type UseQueryOptions,
} from "@tanstack/react-query";

import {
  fetchProductById,
  fetchProductDetails,
  fetchProducts,
  searchProducts,
} from "../services/products.service";
import type { ProductDetail, ProductListParams, ProductListResponse } from "../types/product";
import { isApiError } from "../errors";
import { queryKeys } from "./query-keys";

export function useProducts(
  params?: ProductListParams,
  options?: Omit<
    UseQueryOptions<ProductListResponse, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: queryKeys.products.list(params),
    queryFn: () => fetchProducts(params),
    staleTime: 60_000,
    ...options,
  });
}

export function useInfiniteProducts(
  params?: Omit<ProductListParams, "cursor">,
  options?: Omit<
    UseInfiniteQueryOptions<ProductListResponse, Error>,
    "queryKey" | "queryFn" | "initialPageParam" | "getNextPageParam"
  >
) {
  return useInfiniteQuery({
    queryKey: queryKeys.products.list(params),
    queryFn: ({ pageParam }) =>
      fetchProducts({ ...params, cursor: pageParam as string | null }),
    initialPageParam: null as string | null,
    getNextPageParam: (lastPage) =>
      lastPage.pagination.has_more ? lastPage.pagination.next_cursor : undefined,
    staleTime: 60_000,
    ...options,
  });
}

export function useProductDetails(
  slug: string,
  options?: Omit<UseQueryOptions<ProductDetail, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.products.detail(slug),
    queryFn: () => fetchProductDetails(slug),
    enabled: Boolean(slug),
    staleTime: 120_000,
    ...options,
  });
}

export function useProductById(
  productId: string,
  options?: Omit<UseQueryOptions<ProductDetail, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.products.byId(productId),
    queryFn: () => fetchProductById(productId),
    enabled: Boolean(productId),
    staleTime: 120_000,
    ...options,
  });
}

export function useProductSearch(
  query: string,
  options?: { enabled?: boolean; limit?: number }
) {
  const trimmed = query.trim();
  return useQuery({
    queryKey: queryKeys.products.search(trimmed),
    queryFn: () => searchProducts(trimmed, options?.limit),
    enabled: (options?.enabled ?? true) && trimmed.length >= 2,
    staleTime: 30_000,
    retry: (failureCount, error) => {
      if (isApiError(error) && error.status === 404) return false;
      return failureCount < 2;
    },
  });
}
