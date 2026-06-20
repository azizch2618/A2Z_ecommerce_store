import type { SortOption } from "@/config/category-page";
import { LISTING_PAGE_SIZE } from "@/config/category-page";
import { catalogPage } from "@/config/catalog-page";
import type { CategoryFilterState } from "@/components/category/category-filters";
import type { ProductListParams, ProductSort } from "@/lib/api/types/product";

function mapSortToApi(sort: SortOption): ProductSort {
  switch (sort) {
    case "price-asc":
      return "price_asc";
    case "price-desc":
      return "price_desc";
    case "newest":
      return "newest";
    case "best-selling":
    case "featured":
    default:
      return "featured";
  }
}

export function buildProductListApiParams(options: {
  filters: CategoryFilterState;
  sort: SortOption;
  search?: string;
  cursor?: string | null;
  initialCategory?: string | null;
  initialBrand?: string | null;
}): ProductListParams {
  const category =
    options.filters.categories[0] ?? options.initialCategory ?? undefined;
  const brand = options.filters.brands[0] ?? options.initialBrand ?? undefined;

  let min_price: number | undefined;
  let max_price: number | undefined;
  if (options.filters.priceRanges.length === 1) {
    const range = catalogPage.priceRanges.find(
      (item: { id: string }) => item.id === options.filters.priceRanges[0]
    );
    if (range) {
      min_price = Math.round(range.min * 100);
      if (range.max !== null) {
        max_price = Math.round(range.max * 100);
      }
    }
  }

  let in_stock: boolean | undefined;
  if (options.filters.availability.length === 1) {
    if (options.filters.availability[0] === "in_stock") {
      in_stock = true;
    } else if (options.filters.availability[0] === "out_of_stock") {
      in_stock = false;
    }
  }

  return {
    search: options.search || undefined,
    category,
    brand,
    sort: mapSortToApi(options.sort),
    min_price,
    max_price,
    in_stock,
    cursor: options.cursor ?? undefined,
    limit: LISTING_PAGE_SIZE,
  };
}

export { LISTING_PAGE_SIZE, mapSortToApi };
