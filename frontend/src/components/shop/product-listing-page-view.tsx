"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";
import { useSearchParams } from "next/navigation";

import type { SortOption } from "@/config/category-page";
import { LISTING_PAGE_SIZE } from "@/config/category-page";
import { catalogPage } from "@/config/catalog-page";
import { CategoryFilterSidebar } from "@/components/category/category-filter-sidebar";
import { CategoryMobileFilters } from "@/components/category/category-mobile-filters";
import { CategoryPagination } from "@/components/category/category-pagination";
import { CategoryToolbar } from "@/components/category/category-toolbar";
import type { CategoryFilterState } from "@/components/category/category-filters";
import { ProductListingGrid } from "@/components/product";
import { ListingPageHeader } from "@/components/shop/listing-page-header";
import { Container } from "@/components/layout/container";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
import { Button } from "@/components/ui/button";
import {
  filterCategoryProducts,
  sortCategoryProducts,
} from "@/lib/category-listing";
import { buildProductListApiParams } from "@/lib/category-listing-api";
import { useCursorProductListing } from "@/lib/api/hooks/use-cursor-product-listing";
import { mapApiProductToCategoryProduct } from "@/lib/api/mappers/product-mapper";

const defaultFilters: CategoryFilterState = {
  brands: [],
  priceRanges: [],
  availability: [],
  ratings: [],
  categories: [],
};

function ProductListingPageView() {
  const searchParams = useSearchParams();
  const searchQuery = searchParams.get("q") ?? searchParams.get("search") ?? "";
  const initialCategory = searchParams.get("category");
  const initialBrand = searchParams.get("brand");

  const [filters, setFilters] = React.useState<CategoryFilterState>(() => ({
    ...defaultFilters,
    categories: initialCategory ? [initialCategory] : [],
    brands: initialBrand ? [initialBrand] : [],
  }));
  const [sort, setSort] = React.useState<SortOption>("featured");
  const [viewMode, setViewMode] = React.useState<"grid" | "list">("grid");
  const [mobileFiltersOpen, setMobileFiltersOpen] = React.useState(false);
  const listingRef = React.useRef<HTMLDivElement>(null);

  const resetKey = JSON.stringify({
    filters,
    sort,
    searchQuery,
    initialCategory,
    initialBrand,
  });

  const apiParams = React.useMemo(
    () =>
      buildProductListApiParams({
        filters,
        sort,
        search: searchQuery || undefined,
        initialCategory,
        initialBrand,
      }),
    [filters, sort, searchQuery, initialCategory, initialBrand]
  );

  const { data, isLoading, isError, refetch, currentPage, goToPage, maxPage, hasMore } =
    useCursorProductListing(apiParams, resetKey);

  React.useEffect(() => {
    setFilters((current) => ({
      ...current,
      categories: initialCategory ? [initialCategory] : current.categories,
      brands: initialBrand ? [initialBrand] : current.brands,
    }));
  }, [initialCategory, initialBrand]);

  const pageProducts = React.useMemo(() => {
    const mapped = (data?.data ?? []).map(mapApiProductToCategoryProduct);
    const needsClientFilter =
      filters.brands.length > 1 ||
      filters.categories.length > 1 ||
      filters.priceRanges.length > 1 ||
      filters.availability.length > 1 ||
      filters.ratings.length > 0;

    if (!needsClientFilter) {
      return mapped;
    }

    return sortCategoryProducts(
      filterCategoryProducts(mapped, filters, catalogPage),
      sort
    );
  }, [data?.data, filters, sort]);

  const startIndex = (currentPage - 1) * LISTING_PAGE_SIZE;
  const endIndex = startIndex + pageProducts.length;
  const totalItems = hasMore ? endIndex + 1 : endIndex;
  const totalPages = Math.max(maxPage, currentPage);

  const handlePageChange = (page: number) => {
    goToPage(page);
    listingRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const activeFilterCount =
    filters.brands.length +
    filters.priceRanges.length +
    filters.availability.length +
    filters.ratings.length +
    filters.categories.length;

  const breadcrumbs = [
    { label: "Home", href: "/" },
    {
      label: searchQuery ? `Search: ${searchQuery}` : "All products",
      href: "/products",
    },
  ];

  return (
    <>
      <PageBreadcrumbs items={breadcrumbs} />
      <ListingPageHeader
        page={catalogPage}
        productCount={hasMore ? endIndex + 1 : endIndex}
      />

      <div ref={listingRef}>
        <Container className="pb-16 pt-6 md:pt-8">
          <div className="flex flex-col gap-8 lg:flex-row">
            <CategoryFilterSidebar
              category={catalogPage}
              filters={filters}
              onFiltersChange={setFilters}
              className="hidden lg:block"
            />

            <div className="min-w-0 flex-1">
              <CategoryToolbar
                sort={sort}
                onSortChange={setSort}
                viewMode={viewMode}
                onViewModeChange={setViewMode}
                resultCount={pageProducts.length}
                totalCount={totalItems}
                onOpenFilters={() => setMobileFiltersOpen(true)}
                activeFilterCount={activeFilterCount}
              />

              {isLoading ? (
                <div className="flex min-h-[40vh] items-center justify-center">
                  <Loader2 className="size-8 animate-spin text-brand-blue" />
                </div>
              ) : isError ? (
                <div className="flex min-h-[40vh] flex-col items-center justify-center gap-3 text-center">
                  <p className="font-medium text-brand-navy">Could not load products</p>
                  <p className="text-sm text-muted-foreground">
                    Start the API and run <code className="text-xs">python manage.py seed_demo</code>
                  </p>
                  <Button onClick={() => refetch()}>Retry</Button>
                </div>
              ) : pageProducts.length === 0 ? (
                <div className="rounded-xl border border-dashed border-border py-16 text-center">
                  <p className="text-muted-foreground">No products match your filters.</p>
                </div>
              ) : (
                <>
                  <ProductListingGrid products={pageProducts} layout={viewMode} />
                  <CategoryPagination
                    currentPage={currentPage}
                    totalPages={totalPages}
                    onPageChange={handlePageChange}
                    startIndex={startIndex}
                    endIndex={endIndex}
                    totalItems={totalItems}
                    className="mt-10"
                  />
                </>
              )}
            </div>
          </div>
        </Container>
      </div>

      <CategoryMobileFilters
        open={mobileFiltersOpen}
        onOpenChange={setMobileFiltersOpen}
        category={catalogPage}
        filters={filters}
        onFiltersChange={setFilters}
        resultCount={totalItems}
      />
    </>
  );
}

export { ProductListingPageView };
