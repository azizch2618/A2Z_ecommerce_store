export interface SearchProductResult {
  id: string;
  name: string;
  brand: string;
  sku: string;
  href: string;
  imageSrc: string;
  imageAlt: string;
  priceLabel: string;
}

export interface SearchCategoryResult {
  id: string;
  label: string;
  href: string;
  description: string;
}

export interface SearchBrandResult {
  id: string;
  label: string;
  href: string;
  productCount: string;
}

export interface PredictiveSearchResults {
  products: SearchProductResult[];
  categories: SearchCategoryResult[];
  brands: SearchBrandResult[];
}

export type SearchDropdownItemType =
  | "product"
  | "category"
  | "brand"
  | "recent"
  | "popular";

export interface SearchDropdownItem {
  type: SearchDropdownItemType;
  id: string;
  label: string;
  href?: string;
  query?: string;
  meta?: string;
  imageSrc?: string;
  imageAlt?: string;
}
