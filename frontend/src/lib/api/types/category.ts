import type { ListQueryParams, PaginatedResponse } from "./common";
import type { ProductListParams, ProductSummary } from "./product";

export interface CategoryNode {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  image_url: string | null;
  sort_order: number;
  product_count: number;
  children: CategoryNode[];
  meta_title: string | null;
  meta_description: string | null;
}

export interface CategoryListParams extends ListQueryParams {
  parent?: string;
  depth?: number;
  flat?: boolean;
}

export interface CategoryDetail extends CategoryNode {
  breadcrumbs: Array<{ label: string; slug: string; href: string }>;
  featured_products: ProductSummary[];
}

export type CategoryListResponse = PaginatedResponse<CategoryNode>;

export type CategoryProductsParams = ProductListParams;
