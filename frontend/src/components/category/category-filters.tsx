"use client";

import * as React from "react";
import { X } from "lucide-react";

import type {
  AvailabilityFilter,
  CategoryPageData,
} from "@/config/category-page";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export interface CategoryFilterState {
  brands: string[];
  priceRanges: string[];
  availability: AvailabilityFilter[];
  ratings: string[];
  categories: string[];
}

export interface CategoryFiltersProps {
  category: CategoryPageData;
  filters: CategoryFilterState;
  onFiltersChange: (filters: CategoryFilterState) => void;
  className?: string;
  collapsible?: boolean;
}

function toggleValue<T extends string>(values: T[], value: T): T[] {
  return values.includes(value)
    ? values.filter((item) => item !== value)
    : [...values, value];
}

function CategoryFilters({
  category,
  filters,
  onFiltersChange,
  className,
  collapsible = true,
}: CategoryFiltersProps) {
  const activeCount =
    filters.brands.length +
    filters.priceRanges.length +
    filters.availability.length +
    filters.ratings.length +
    filters.categories.length;

  const clearAll = () => {
    onFiltersChange({
      brands: [],
      priceRanges: [],
      availability: [],
      ratings: [],
      categories: [],
    });
  };

  const brandList = (
    <ul className="space-y-3">
      {category.brands.map((brand) => {
        const checked = filters.brands.includes(brand.id);
        return (
          <li key={brand.id}>
            <label className="flex cursor-pointer items-center gap-3">
              <Checkbox
                checked={checked}
                onCheckedChange={() =>
                  onFiltersChange({
                    ...filters,
                    brands: toggleValue(filters.brands, brand.id),
                  })
                }
                aria-label={`Filter by ${brand.label}`}
              />
              <span className="flex flex-1 items-center justify-between gap-2 text-sm">
                <span className={cn(checked && "font-medium text-brand-navy")}>
                  {brand.label}
                </span>
                <span className="text-xs tabular-nums text-muted-foreground">
                  {brand.count}
                </span>
              </span>
            </label>
          </li>
        );
      })}
    </ul>
  );

  const priceList = (
    <ul className="space-y-3">
      {category.priceRanges.map((range) => {
        const checked = filters.priceRanges.includes(range.id);
        return (
          <li key={range.id}>
            <label className="flex cursor-pointer items-center gap-3">
              <Checkbox
                checked={checked}
                onCheckedChange={() =>
                  onFiltersChange({
                    ...filters,
                    priceRanges: toggleValue(filters.priceRanges, range.id),
                  })
                }
                aria-label={`Filter by ${range.label}`}
              />
              <span
                className={cn(
                  "text-sm",
                  checked && "font-medium text-brand-navy"
                )}
              >
                {range.label}
              </span>
            </label>
          </li>
        );
      })}
    </ul>
  );

  const availabilityList = (
    <ul className="space-y-3">
      {category.availabilityOptions.map((option) => {
        const checked = filters.availability.includes(option.id);
        return (
          <li key={option.id}>
            <label className="flex cursor-pointer items-center gap-3">
              <Checkbox
                checked={checked}
                onCheckedChange={() =>
                  onFiltersChange({
                    ...filters,
                    availability: toggleValue(filters.availability, option.id),
                  })
                }
                aria-label={`Filter by ${option.label}`}
              />
              <span
                className={cn(
                  "text-sm",
                  checked && "font-medium text-brand-navy"
                )}
              >
                {option.label}
              </span>
            </label>
          </li>
        );
      })}
    </ul>
  );

  const ratingList = (
    <ul className="space-y-3">
      {category.ratingOptions.map((option) => {
        const checked = filters.ratings.includes(option.id);
        return (
          <li key={option.id}>
            <label className="flex cursor-pointer items-center gap-3">
              <Checkbox
                checked={checked}
                onCheckedChange={() =>
                  onFiltersChange({
                    ...filters,
                    ratings: toggleValue(filters.ratings, option.id),
                  })
                }
                aria-label={`Filter by ${option.label}`}
              />
              <span
                className={cn(
                  "text-sm",
                  checked && "font-medium text-brand-navy"
                )}
              >
                {option.label}
              </span>
            </label>
          </li>
        );
      })}
    </ul>
  );

  const categoryList = category.categories ? (
    <ul className="space-y-3">
      {category.categories.map((item) => {
        const checked = filters.categories.includes(item.id);
        return (
          <li key={item.id}>
            <label className="flex cursor-pointer items-center gap-3">
              <Checkbox
                checked={checked}
                onCheckedChange={() =>
                  onFiltersChange({
                    ...filters,
                    categories: toggleValue(filters.categories, item.id),
                  })
                }
                aria-label={`Filter by ${item.label}`}
              />
              <span className="flex flex-1 items-center justify-between gap-2 text-sm">
                <span className={cn(checked && "font-medium text-brand-navy")}>
                  {item.label}
                </span>
                <span className="text-xs tabular-nums text-muted-foreground">
                  {item.count}
                </span>
              </span>
            </label>
          </li>
        );
      })}
    </ul>
  ) : null;

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-[0.12em] text-brand-navy">
            Filters
          </h2>
          {activeCount > 0 ? (
            <p className="mt-0.5 text-xs text-muted-foreground">
              {activeCount} active
            </p>
          ) : null}
        </div>
        {activeCount > 0 ? (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-8 gap-1 px-2 text-brand-blue"
            onClick={clearAll}
          >
            <X className="size-3.5" />
            Clear all
          </Button>
        ) : null}
      </div>

      {collapsible ? (
        <Accordion
          type="multiple"
          defaultValue={[
            "category",
            "brand",
            "price",
            "availability",
            "rating",
          ].filter((value) => value !== "category" || category.categories)}
        >
          {category.categories ? (
            <AccordionItem value="category" className="border-border">
              <AccordionTrigger className="py-3 text-sm font-semibold text-brand-navy hover:no-underline">
                Category
              </AccordionTrigger>
              <AccordionContent className="pb-4">{categoryList}</AccordionContent>
            </AccordionItem>
          ) : null}
          <AccordionItem value="brand" className="border-border">
            <AccordionTrigger className="py-3 text-sm font-semibold text-brand-navy hover:no-underline">
              Brand
            </AccordionTrigger>
            <AccordionContent className="pb-4">{brandList}</AccordionContent>
          </AccordionItem>
          <AccordionItem value="price" className="border-border">
            <AccordionTrigger className="py-3 text-sm font-semibold text-brand-navy hover:no-underline">
              Price
            </AccordionTrigger>
            <AccordionContent className="pb-4">{priceList}</AccordionContent>
          </AccordionItem>
          <AccordionItem value="availability" className="border-border">
            <AccordionTrigger className="py-3 text-sm font-semibold text-brand-navy hover:no-underline">
              Availability
            </AccordionTrigger>
            <AccordionContent className="pb-4">{availabilityList}</AccordionContent>
          </AccordionItem>
          <AccordionItem value="rating" className="border-border">
            <AccordionTrigger className="py-3 text-sm font-semibold text-brand-navy hover:no-underline">
              Rating
            </AccordionTrigger>
            <AccordionContent className="pb-4">{ratingList}</AccordionContent>
          </AccordionItem>
        </Accordion>
      ) : (
        <div className="space-y-6">
          {category.categories ? (
            <>
              <div className="space-y-4">
                <Label className="text-sm font-semibold text-brand-navy">Category</Label>
                {categoryList}
              </div>
              <Separator />
            </>
          ) : null}
          <div className="space-y-4">
            <Label className="text-sm font-semibold text-brand-navy">Brand</Label>
            {brandList}
          </div>
          <Separator />
          <div className="space-y-4">
            <Label className="text-sm font-semibold text-brand-navy">Price</Label>
            {priceList}
          </div>
          <Separator />
          <div className="space-y-4">
            <Label className="text-sm font-semibold text-brand-navy">Availability</Label>
            {availabilityList}
          </div>
          <Separator />
          <div className="space-y-4">
            <Label className="text-sm font-semibold text-brand-navy">Rating</Label>
            {ratingList}
          </div>
        </div>
      )}
    </div>
  );
}

export { CategoryFilters };
