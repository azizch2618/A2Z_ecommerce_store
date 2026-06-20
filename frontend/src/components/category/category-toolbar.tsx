"use client";

import { LayoutGrid, List, SlidersHorizontal } from "lucide-react";

import type { SortOption } from "@/config/category-page";
import { sortOptions } from "@/config/category-page";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export interface CategoryToolbarProps {
  resultCount: number;
  totalCount: number;
  sort: SortOption;
  onSortChange: (sort: SortOption) => void;
  viewMode: "grid" | "list";
  onViewModeChange: (mode: "grid" | "list") => void;
  onOpenFilters?: () => void;
  activeFilterCount?: number;
  className?: string;
}

function CategoryToolbar({
  resultCount,
  totalCount,
  sort,
  onSortChange,
  viewMode,
  onViewModeChange,
  onOpenFilters,
  activeFilterCount = 0,
  className,
}: CategoryToolbarProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-4 rounded-xl border border-border bg-card p-4 shadow-sm lg:flex-row lg:items-center lg:justify-between",
        className
      )}
    >
      <div className="flex flex-wrap items-center gap-3">
        {onOpenFilters ? (
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="gap-2 lg:hidden"
            onClick={onOpenFilters}
          >
            <SlidersHorizontal className="size-4" />
            Filters
            {activeFilterCount > 0 ? (
              <span className="flex size-5 items-center justify-center rounded-full bg-brand-blue text-[10px] font-bold text-white">
                {activeFilterCount}
              </span>
            ) : null}
          </Button>
        ) : null}
        <p className="text-sm text-muted-foreground">
          <span className="font-semibold text-brand-navy">{resultCount}</span>{" "}
          {resultCount === 1 ? "product" : "products"}
          {totalCount !== resultCount ? (
            <>
              {" "}
              <span className="text-muted-foreground">of {totalCount}</span>
            </>
          ) : null}
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="flex items-center gap-2">
          <span className="shrink-0 text-sm font-medium text-brand-navy">View</span>
          <div className="flex rounded-lg border border-border p-0.5">
            <Button
              type="button"
              variant={viewMode === "grid" ? "secondary" : "ghost"}
              size="icon-sm"
              className="size-8"
              onClick={() => onViewModeChange("grid")}
              aria-label="Grid view"
              aria-pressed={viewMode === "grid"}
            >
              <LayoutGrid className="size-4" />
            </Button>
            <Button
              type="button"
              variant={viewMode === "list" ? "secondary" : "ghost"}
              size="icon-sm"
              className="size-8"
              onClick={() => onViewModeChange("list")}
              aria-label="List view"
              aria-pressed={viewMode === "list"}
            >
              <List className="size-4" />
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <label htmlFor="category-sort" className="shrink-0 text-sm font-medium text-brand-navy">
            Sort by
          </label>
          <Select value={sort} onValueChange={(value) => onSortChange(value as SortOption)}>
            <SelectTrigger id="category-sort" className="w-full min-w-[200px] sm:w-52">
              <SelectValue placeholder="Sort products" />
            </SelectTrigger>
            <SelectContent>
              {sortOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}

export { CategoryToolbar };
