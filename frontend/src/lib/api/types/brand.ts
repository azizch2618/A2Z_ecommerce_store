import type { PaginatedResponse } from "./common";
import type { ProductListParams, ProductSummary } from "./product";

export interface BrandSummary {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  logo_url: string | null;
  product_count: number;
  is_authorized_reseller: boolean;
}

export interface BrandDetail extends BrandSummary {
  website_url: string | null;
  featured_products: ProductSummary[];
}

export type BrandListResponse = PaginatedResponse<BrandSummary>;

export type BrandProductsParams = ProductListParams;
