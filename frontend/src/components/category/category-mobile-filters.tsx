"use client";

import * as React from "react";

import type { CategoryPageData } from "@/config/category-page";
import { CategoryFilters, type CategoryFilterState } from "@/components/category/category-filters";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

export interface CategoryMobileFiltersProps {
  category: CategoryPageData;
  filters: CategoryFilterState;
  onFiltersChange: (filters: CategoryFilterState) => void;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  resultCount: number;
}

function CategoryMobileFilters({
  category,
  filters,
  onFiltersChange,
  open,
  onOpenChange,
  resultCount,
}: CategoryMobileFiltersProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="flex w-full flex-col sm:max-w-md">
        <SheetHeader className="border-b border-border pb-4 text-left">
          <SheetTitle className="text-brand-navy">Filter products</SheetTitle>
        </SheetHeader>

        <div className="flex-1 overflow-y-auto py-4">
          <CategoryFilters
            category={category}
            filters={filters}
            onFiltersChange={onFiltersChange}
            collapsible
          />
        </div>

        <SheetFooter className="border-t border-border pt-4">
          <Button
            type="button"
            className="w-full"
            onClick={() => onOpenChange(false)}
          >
            Show {resultCount} products
          </Button>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
}

export { CategoryMobileFilters };
