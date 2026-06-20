import { apiGet, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  ProductDetail,
  ProductListParams,
  ProductListResponse,
  ProductSearchResponse,
} from "../types/product";

function buildQueryParams(
  params?: ProductListParams
): Record<string, string | number | boolean> {
  if (!params) return {};
  const query: Record<string, string | number | boolean> = {};
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      query[key] = value;
    }
  }
  return query;
}

/** List products with cursor pagination and filters */
export async function fetchProducts(
  params?: ProductListParams
): Promise<ProductListResponse> {
  return apiGet<ProductListResponse>(API_ENDPOINTS.products.list, {
    params: buildQueryParams(params),
  });
}

/** Full product detail by URL slug (PDP) */
export async function fetchProductDetails(
  slug: string
): Promise<ProductDetail> {
  return apiGet<ProductDetail>(API_ENDPOINTS.products.bySlug(slug));
}

/** Product detail by public UUID */
export async function fetchProductById(
  productId: string
): Promise<ProductDetail> {
  return apiGet<ProductDetail>(API_ENDPOINTS.products.byId(productId));
}

/** Predictive / autocomplete search */
export async function searchProducts(
  query: string,
  limit = 8
): Promise<ProductSearchResponse> {
  return apiGet<ProductSearchResponse>(API_ENDPOINTS.products.search, {
    params: { q: query, limit },
  });
}

/** Side-by-side product comparison */
export async function compareProducts(
  productIds: string[]
): Promise<{ products: ProductDetail[]; comparison_attributes: Array<{ key: string; label: string }> }> {
  return apiPost(API_ENDPOINTS.products.compare, { product_ids: productIds });
}
