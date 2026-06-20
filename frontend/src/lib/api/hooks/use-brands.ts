"use client";

import { useQuery, type UseQueryOptions } from "@tanstack/react-query";

import {
  fetchBrandBySlug,
  fetchBrandProducts,
  fetchBrands,
} from "../services/brands.service";
import type {
  BrandDetail,
  BrandListResponse,
  BrandProductsParams,
} from "../types/brand";
import type { ListQueryParams } from "../types/common";
import type { ProductListResponse } from "../types/product";
import { queryKeys } from "./query-keys";

export function useBrands(
  params?: ListQueryParams,
  options?: Omit<
    UseQueryOptions<BrandListResponse, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: queryKeys.brands.list(params),
    queryFn: () => fetchBrands(params),
    staleTime: 300_000,
    ...options,
  });
}

export function useBrand(
  slug: string,
  options?: Omit<UseQueryOptions<BrandDetail, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.brands.detail(slug),
    queryFn: () => fetchBrandBySlug(slug),
    enabled: Boolean(slug),
    staleTime: 300_000,
    ...options,
  });
}

export function useBrandProducts(
  slug: string,
  params?: BrandProductsParams,
  options?: Omit<
    UseQueryOptions<ProductListResponse, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: queryKeys.brands.products(slug, params),
    queryFn: () => fetchBrandProducts(slug, params),
    enabled: Boolean(slug),
    staleTime: 60_000,
    ...options,
  });
}
