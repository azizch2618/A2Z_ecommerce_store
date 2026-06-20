"use client";

import * as React from "react";

import type {
  CategoryPageData,
  CategoryProduct,
  SortOption,
} from "@/config/category-page";
import {
  networkingCategory,
  networkingProducts,
} from "@/config/category-page";
import { CategoryBanner } from "@/components/category/category-banner";
import { CategoryDescription } from "@/components/category/category-description";
import { CategoryFeaturedBrands } from "@/components/category/category-featured-brands";
import { CategoryFilterSidebar } from "@/components/category/category-filter-sidebar";
import { CategoryMobileFilters } from "@/components/category/category-mobile-filters";
import { CategoryPagination } from "@/components/category/category-pagination";
import { CategoryToolbar } from "@/components/category/category-toolbar";
import type { CategoryFilterState } from "@/components/category/category-filters";
import { ProductListingGrid } from "@/components/product";
import { Container } from "@/components/layout/container";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
import { Button } from "@/components/ui/button";
import {
  filterCategoryProducts,
  paginateProducts,
  sortCategoryProducts,
} from "@/lib/category-listing";

export interface CategoryPageViewProps {
  category?: CategoryPageData;
  products?: CategoryProduct[];
}

const defaultFilters: CategoryFilterState = {
  brands: [],
  priceRanges: [],
  availability: [],
  ratings: [],
  categories: [],
};

function CategoryPageView({
  category = networkingCategory,
  products = networkingProducts,
}: CategoryPageViewProps) {
  const [filters, setFilters] = React.useState<CategoryFilterState>(defaultFilters);
  const [sort, setSort] = React.useState<SortOption>("featured");
  const [viewMode, setViewMode] = React.useState<"grid" | "list">("grid");
  const [currentPage, setCurrentPage] = React.useState(1);
  const [mobileFiltersOpen, setMobileFiltersOpen] = React.useState(false);
  const listingRef = React.useRef<HTMLDivElement>(null);

  const filtered = React.useMemo(
    () => sortCategoryProducts(filterCategoryProducts(products, filters, category), sort),
    [products, filters, category, sort]
  );

  const paginated = React.useMemo(
    () => paginateProducts(filtered, currentPage),
    [filtered, currentPage]
  );

  React.useEffect(() => {
    setCurrentPage(1);
  }, [filters, sort]);

  React.useEffect(() => {
    if (currentPage > paginated.totalPages) {
      setCurrentPage(paginated.totalPages);
    }
  }, [currentPage, paginated.totalPages]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    listingRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleBrandSelect = (brandId: string) => {
    setFilters((current) => {
      const hasBrand = current.brands.includes(brandId);
      return {
        ...current,
        brands: hasBrand
          ? current.brands.filter((id) => id !== brandId)
          : [...current.brands, brandId],
      };
    });
    listingRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const activeFilterCount =
    filters.brands.length +
    filters.priceRanges.length +
    filters.availability.length +
    filters.ratings.length +
    filters.categories.length;

  return (
    <>
      <PageBreadcrumbs items={category.breadcrumbs} />
      <CategoryBanner category={category} />
      <CategoryDescription category={category} />
      <CategoryFeaturedBrands
        brands={category.featuredBrands}
        onBrandSelect={handleBrandSelect}
        activeBrandIds={filters.brands}
      />

      <div ref={listingRef} className="scroll-mt-24">
        <Container className="py-8 md:py-10">
        <div className="grid gap-8 lg:grid-cols-[280px_minmax(0,1fr)] lg:gap-10">
          <CategoryFilterSidebar
            category={category}
            filters={filters}
            onFiltersChange={setFilters}
          />

          <div className="min-w-0 space-y-6">
            <CategoryToolbar
              resultCount={filtered.length}
              totalCount={products.length}
              sort={sort}
              onSortChange={setSort}
              viewMode={viewMode}
              onViewModeChange={setViewMode}
              onOpenFilters={() => setMobileFiltersOpen(true)}
              activeFilterCount={activeFilterCount}
            />

            {activeFilterCount > 0 ? (
              <div className="flex flex-wrap items-center gap-2">
                {filters.brands.map((brandId) => {
                  const brand = category.brands.find((item) => item.id === brandId);
                  return brand ? (
                    <button
                      key={brandId}
                      type="button"
                      onClick={() =>
                        setFilters((current) => ({
                          ...current,
                          brands: current.brands.filter((id) => id !== brandId),
                        }))
                      }
                      className="rounded-full border border-brand-blue/30 bg-brand-blue-light/50 px-3 py-1 text-xs font-medium text-brand-blue transition-colors hover:bg-brand-blue-light"
                    >
                      {brand.label} ×
                    </button>
                  ) : null;
                })}
                <button
                  type="button"
                  onClick={() => setFilters(defaultFilters)}
                  className="text-xs font-medium text-muted-foreground hover:text-brand-blue"
                >
                  Clear all
                </button>
              </div>
            ) : null}

            {filtered.length === 0 ? (
              <div className="rounded-xl border border-dashed border-border bg-neutral-50 px-6 py-16 text-center">
                <p className="text-lg font-semibold text-brand-navy">
                  No products match your filters
                </p>
                <p className="mt-2 text-sm text-muted-foreground">
                  Try adjusting brand, price, availability, or rating selections.
                </p>
                <Button
                  type="button"
                  variant="outline"
                  className="mt-6"
                  onClick={() => setFilters(defaultFilters)}
                >
                  Clear all filters
                </Button>
              </div>
            ) : (
              <>
                <ProductListingGrid products={paginated.items} layout={viewMode} />
                <CategoryPagination
                  currentPage={paginated.currentPage}
                  totalPages={paginated.totalPages}
                  onPageChange={handlePageChange}
                  startIndex={paginated.startIndex}
                  endIndex={paginated.endIndex}
                  totalItems={paginated.totalItems}
                />
              </>
            )}
          </div>
        </div>
        </Container>
      </div>

      <CategoryMobileFilters
        category={category}
        filters={filters}
        onFiltersChange={setFilters}
        open={mobileFiltersOpen}
        onOpenChange={setMobileFiltersOpen}
        resultCount={filtered.length}
      />
    </>
  );
}

export { CategoryPageView };
