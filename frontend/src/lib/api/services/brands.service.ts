import { apiGet } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  BrandDetail,
  BrandListResponse,
  BrandProductsParams,
} from "../types/brand";
import type { ProductListResponse } from "../types/product";
import type { ListQueryParams } from "../types/common";

/** Brand directory */
export async function fetchBrands(
  params?: ListQueryParams
): Promise<BrandListResponse> {
  return apiGet<BrandListResponse>(API_ENDPOINTS.brands.list, { params });
}

/** Brand detail page */
export async function fetchBrandBySlug(slug: string): Promise<BrandDetail> {
  return apiGet<BrandDetail>(API_ENDPOINTS.brands.bySlug(slug));
}

/** Products for a brand */
export async function fetchBrandProducts(
  slug: string,
  params?: BrandProductsParams
): Promise<ProductListResponse> {
  return apiGet<ProductListResponse>(API_ENDPOINTS.brands.products(slug), {
    params,
  });
}
