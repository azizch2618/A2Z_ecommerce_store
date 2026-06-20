import { apiGet } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  CategoryDetail,
  CategoryListParams,
  CategoryListResponse,
  CategoryProductsParams,
} from "../types/category";
import type { ProductListResponse } from "../types/product";

/** Category tree for navigation */
export async function fetchCategories(
  params?: CategoryListParams
): Promise<CategoryListResponse> {
  return apiGet<CategoryListResponse>(API_ENDPOINTS.categories.list, {
    params,
  });
}

/** Category landing page by slug */
export async function fetchCategoryBySlug(
  slug: string
): Promise<CategoryDetail> {
  return apiGet<CategoryDetail>(API_ENDPOINTS.categories.bySlug(slug));
}

/** Products within a category */
export async function fetchCategoryProducts(
  slug: string,
  params?: CategoryProductsParams
): Promise<ProductListResponse> {
  return apiGet<ProductListResponse>(
    API_ENDPOINTS.categories.products(slug),
    { params }
  );
}
