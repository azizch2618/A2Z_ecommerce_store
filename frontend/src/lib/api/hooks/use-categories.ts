"use client";

import { useQuery, type UseQueryOptions } from "@tanstack/react-query";

import {
  fetchCategories,
  fetchCategoryBySlug,
  fetchCategoryProducts,
} from "../services/categories.service";
import type {
  CategoryDetail,
  CategoryListParams,
  CategoryListResponse,
  CategoryProductsParams,
} from "../types/category";
import type { ProductListResponse } from "../types/product";
import { queryKeys } from "./query-keys";

export function useCategories(
  params?: CategoryListParams,
  options?: Omit<
    UseQueryOptions<CategoryListResponse, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: queryKeys.categories.list(params),
    queryFn: () => fetchCategories(params),
    staleTime: 300_000,
    ...options,
  });
}

export function useCategory(
  slug: string,
  options?: Omit<UseQueryOptions<CategoryDetail, Error>, "queryKey" | "queryFn">
) {
  return useQuery({
    queryKey: queryKeys.categories.detail(slug),
    queryFn: () => fetchCategoryBySlug(slug),
    enabled: Boolean(slug),
    staleTime: 300_000,
    ...options,
  });
}

export function useCategoryProducts(
  slug: string,
  params?: CategoryProductsParams,
  options?: Omit<
    UseQueryOptions<ProductListResponse, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: queryKeys.categories.products(slug, params),
    queryFn: () => fetchCategoryProducts(slug, params),
    enabled: Boolean(slug),
    staleTime: 60_000,
    ...options,
  });
}
