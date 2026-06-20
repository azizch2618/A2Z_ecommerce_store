"use client";

import * as React from "react";

import type { CategoryPageData } from "@/config/category-page";
import { CategoryFilters, type CategoryFilterState } from "@/components/category/category-filters";
import { cn } from "@/lib/utils";

export interface CategoryFilterSidebarProps {
  category: CategoryPageData;
  filters: CategoryFilterState;
  onFiltersChange: (filters: CategoryFilterState) => void;
  className?: string;
}

function CategoryFilterSidebar({
  category,
  filters,
  onFiltersChange,
  className,
}: CategoryFilterSidebarProps) {
  return (
    <aside
      className={cn("hidden lg:block", className)}
      aria-label="Product filters"
    >
      <div className="sticky top-24 rounded-xl border border-border bg-card p-5 shadow-sm">
        <CategoryFilters
          category={category}
          filters={filters}
          onFiltersChange={onFiltersChange}
          collapsible={false}
        />
      </div>
    </aside>
  );
}

export { CategoryFilterSidebar };
