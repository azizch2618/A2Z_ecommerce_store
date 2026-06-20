import type {
  CategoryPageData,
  CategoryProduct,
  SortOption,
} from "@/config/category-page";
import { LISTING_PAGE_SIZE } from "@/config/category-page";
import type { CategoryFilterState } from "@/components/category/category-filters";
import { brandIdFromLabel } from "@/config/category-page";

function matchesPriceRange(
  price: number,
  rangeId: string,
  category: CategoryPageData
): boolean {
  const range = category.priceRanges.find((item) => item.id === rangeId);
  if (!range) return false;
  if (range.max === null) return price >= range.min;
  return price >= range.min && price <= range.max;
}

function matchesRating(
  productRating: number,
  ratingIds: string[],
  category: CategoryPageData
): boolean {
  return ratingIds.some((id) => {
    const option = category.ratingOptions.find((item) => item.id === id);
    return option ? productRating >= option.min : false;
  });
}

export function filterCategoryProducts(
  products: CategoryProduct[],
  filters: CategoryFilterState,
  category: CategoryPageData
): CategoryProduct[] {
  return products.filter((product) => {
    const brandId = brandIdFromLabel(product.brand);

    if (filters.brands.length > 0 && !filters.brands.includes(brandId)) {
      return false;
    }

    if (
      filters.priceRanges.length > 0 &&
      !filters.priceRanges.some((rangeId) =>
        matchesPriceRange(product.priceValue, rangeId, category)
      )
    ) {
      return false;
    }

    if (
      filters.availability.length > 0 &&
      !filters.availability.includes(product.availability)
    ) {
      return false;
    }

    if (
      filters.ratings.length > 0 &&
      !matchesRating(product.rating, filters.ratings, category)
    ) {
      return false;
    }

    if (
      filters.categories.length > 0 &&
      product.categoryId &&
      !filters.categories.includes(product.categoryId)
    ) {
      return false;
    }

    return true;
  });
}

export function sortCategoryProducts(
  products: CategoryProduct[],
  sort: SortOption
): CategoryProduct[] {
  const sorted = [...products];

  switch (sort) {
    case "featured":
      return sorted.sort((a, b) => {
        const aFeatured = a.featured ? 1 : 0;
        const bFeatured = b.featured ? 1 : 0;
        if (bFeatured !== aFeatured) return bFeatured - aFeatured;
        return b.popularity - a.popularity;
      });
    case "best-selling":
      return sorted.sort((a, b) => b.popularity - a.popularity);
    case "price-asc":
      return sorted.sort((a, b) => a.priceValue - b.priceValue);
    case "price-desc":
      return sorted.sort((a, b) => b.priceValue - a.priceValue);
    case "newest":
      return sorted.sort(
        (a, b) =>
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      );
    default:
      return sorted;
  }
}

export function paginateProducts<T>(
  products: T[],
  page: number,
  pageSize: number = LISTING_PAGE_SIZE
): {
  items: T[];
  totalPages: number;
  currentPage: number;
  totalItems: number;
  startIndex: number;
  endIndex: number;
} {
  const totalItems = products.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const currentPage = Math.min(Math.max(1, page), totalPages);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalItems);

  return {
    items: products.slice(startIndex, endIndex),
    totalPages,
    currentPage,
    totalItems,
    startIndex,
    endIndex,
  };
}

export { LISTING_PAGE_SIZE };
