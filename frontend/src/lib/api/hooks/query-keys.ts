import type { BrandProductsParams } from "../types/brand";
import type { CategoryListParams, CategoryProductsParams } from "../types/category";
import type { ListQueryParams } from "../types/common";
import type { OrderListParams } from "../types/order";
import type { ProductListParams } from "../types/product";
import type { QuoteListParams } from "../types/trade-account";

/**
 * Centralised React Query keys — enables cache invalidation across ERP modules.
 * Pattern: [domain, ...scope, ...params]
 */
export const queryKeys = {
  auth: {
    all: ["auth"] as const,
    me: () => [...queryKeys.auth.all, "me"] as const,
    addresses: () => [...queryKeys.auth.all, "addresses"] as const,
  },
  products: {
    all: ["products"] as const,
    lists: () => [...queryKeys.products.all, "list"] as const,
    list: (params?: ProductListParams) =>
      [...queryKeys.products.lists(), params ?? {}] as const,
    details: () => [...queryKeys.products.all, "detail"] as const,
    detail: (slug: string) =>
      [...queryKeys.products.details(), slug] as const,
    byId: (id: string) =>
      [...queryKeys.products.details(), "id", id] as const,
    search: (query: string) =>
      [...queryKeys.products.all, "search", query] as const,
  },
  categories: {
    all: ["categories"] as const,
    lists: () => [...queryKeys.categories.all, "list"] as const,
    list: (params?: CategoryListParams) =>
      [...queryKeys.categories.lists(), params ?? {}] as const,
    detail: (slug: string) =>
      [...queryKeys.categories.all, "detail", slug] as const,
    products: (slug: string, params?: CategoryProductsParams) =>
      [...queryKeys.categories.all, slug, "products", params ?? {}] as const,
  },
  brands: {
    all: ["brands"] as const,
    lists: () => [...queryKeys.brands.all, "list"] as const,
    list: (params?: ListQueryParams) =>
      [...queryKeys.brands.lists(), params ?? {}] as const,
    detail: (slug: string) =>
      [...queryKeys.brands.all, "detail", slug] as const,
    products: (slug: string, params?: BrandProductsParams) =>
      [...queryKeys.brands.all, slug, "products", params ?? {}] as const,
  },
  cart: {
    all: ["cart"] as const,
    current: () => [...queryKeys.cart.all, "current"] as const,
  },
  wishlist: {
    all: ["wishlist"] as const,
    current: () => [...queryKeys.wishlist.all, "current"] as const,
  },
  orders: {
    all: ["orders"] as const,
    lists: () => [...queryKeys.orders.all, "list"] as const,
    list: (params?: OrderListParams) =>
      [...queryKeys.orders.lists(), params ?? {}] as const,
    detail: (orderId: string) =>
      [...queryKeys.orders.all, "detail", orderId] as const,
  },
  payments: {
    all: ["payments"] as const,
    config: () => [...queryKeys.payments.all, "config"] as const,
  },
  tradeAccounts: {
    all: ["trade-accounts"] as const,
    me: () => [...queryKeys.tradeAccounts.all, "me"] as const,
    quotes: (params?: QuoteListParams) =>
      [...queryKeys.tradeAccounts.all, "quotes", params ?? {}] as const,
    quote: (quoteId: string) =>
      [...queryKeys.tradeAccounts.all, "quote", quoteId] as const,
  },
} as const;
