import type {
  BrandRef,
  ImageRef,
  ListQueryParams,
  PaginatedResponse,
  PriceBlock,
  StockBlock,
} from "./common";

export type ProductSort =
  | "relevance"
  | "price_asc"
  | "price_desc"
  | "newest"
  | "name"
  | "featured";

export interface ProductListParams extends ListQueryParams {
  category?: string;
  brand?: string;
  search?: string;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
  sort?: ProductSort;
}

export interface ProductSummary {
  id: string;
  name: string;
  slug: string;
  short_description: string | null;
  brand: BrandRef;
  primary_image: ImageRef | null;
  default_variant: {
    id: string;
    sku: string;
    price?: PriceBlock;
    stock?: StockBlock;
  } | null;
  price: PriceBlock;
  stock: StockBlock;
  badges: string[];
  average_rating: number | null;
  review_count: number;
}

export interface ProductVariant {
  id: string;
  sku: string;
  barcode: string | null;
  name: string | null;
  price: PriceBlock;
  stock: StockBlock;
  weight_grams: number | null;
  dimensions: {
    length_mm: number | null;
    width_mm: number | null;
    height_mm: number | null;
  } | null;
  attributes: Array<{ name: string; value: string; unit: string | null }>;
  is_default: boolean;
}

export interface ProductDetail {
  id: string;
  name: string;
  slug: string;
  description: string;
  short_description: string | null;
  product_type: "simple" | "variable" | "bundle";
  visibility: string;
  brand: BrandRef;
  categories: Array<{
    id: string;
    name: string;
    slug: string;
    is_primary: boolean;
  }>;
  images: Array<{
    id: string;
    url: string;
    alt_text: string | null;
    sort_order: number;
    is_primary: boolean;
  }>;
  documents: Array<{
    id: string;
    title: string;
    document_type: string;
    url: string;
  }>;
  variants: ProductVariant[];
  attributes: Array<{
    group: string;
    items: Array<{ name: string; value: string }>;
  }>;
  related_products: ProductSummary[];
  highlights?: string[];
  reviews?: Array<{
    id: number;
    author_name: string;
    author_company: string;
    author_role: string;
    rating: number;
    title: string;
    body: string;
    is_verified_purchase: boolean;
    created_at: string;
  }>;
  meta_title: string | null;
  meta_description: string | null;
  average_rating: number;
  review_count: number;
}

export interface ProductListResponse extends PaginatedResponse<ProductSummary> {
  facets?: {
    brands?: Array<{ id: string; name: string; count: number }>;
    categories?: Array<{ id: string; name: string; count: number }>;
  };
}

export interface ProductSearchResponse {
  query: string;
  products: Array<{
    id: string;
    name: string;
    slug: string;
    sku: string;
    image_url: string | null;
    price: PriceBlock;
  }>;
  categories: Array<{ id: string; name: string; slug: string }>;
  brands: Array<{ id: string; name: string; slug: string }>;
}
