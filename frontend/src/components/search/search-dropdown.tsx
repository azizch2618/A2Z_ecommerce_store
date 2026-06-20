"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import type { Route } from "next";
import { Clock, FolderOpen, Package, Search, Store, TrendingUp } from "lucide-react";

import type { PredictiveSearchResults, SearchDropdownItem } from "@/types/search";
import { SearchHighlight } from "@/components/search/search-highlight";
import { RemoteImage } from "@/components/ui/remote-image";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export interface SearchDropdownProps {
  id: string;
  query: string;
  isLoading: boolean;
  results: PredictiveSearchResults;
  recentSearches: string[];
  popularSearches: readonly string[];
  flatItems: SearchDropdownItem[];
  activeIndex: number;
  hasQuery: boolean;
  showNoResults: boolean;
  onSelectItem: (item: SearchDropdownItem) => void;
  onSelectQuery: (query: string) => void;
  onClearRecent: () => void;
  className?: string;
}

function getFlatIndex(
  flatItems: SearchDropdownItem[],
  type: SearchDropdownItem["type"],
  id: string
): number {
  return flatItems.findIndex((item) => item.type === type && item.id === id);
}

function SearchDropdownSection({
  title,
  icon: Icon,
  children,
  action,
}: {
  title: string;
  icon: typeof Package;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="border-b border-border last:border-b-0">
      <div className="flex items-center justify-between px-4 py-2.5">
        <div className="flex items-center gap-2">
          <Icon className="size-3.5 text-brand-blue" aria-hidden />
          <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
            {title}
          </p>
        </div>
        {action}
      </div>
      <ul>{children}</ul>
    </div>
  );
}

function SearchDropdownRow({
  item,
  query,
  isActive,
  onSelect,
}: {
  item: SearchDropdownItem;
  query: string;
  isActive: boolean;
  onSelect: () => void;
}) {
  const content = (
    <>
      {item.type === "product" && item.imageSrc ? (
        <div className="relative size-10 shrink-0 overflow-hidden rounded-md border border-border bg-muted">
          <RemoteImage
            src={item.imageSrc}
            alt={item.imageAlt ?? item.label}
            fill
            sizes="40px"
            className="object-cover"
          />
        </div>
      ) : (
        <span className="flex size-10 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground">
          {item.type === "category" ? (
            <FolderOpen className="size-4" />
          ) : item.type === "brand" ? (
            <Store className="size-4" />
          ) : item.type === "recent" ? (
            <Clock className="size-4" />
          ) : (
            <TrendingUp className="size-4" />
          )}
        </span>
      )}
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-medium text-foreground">
          <SearchHighlight text={item.label} query={query || item.label} />
        </span>
        {item.meta ? (
          <span className="mt-0.5 block truncate text-xs text-muted-foreground">
            {item.meta}
          </span>
        ) : null}
      </span>
    </>
  );

  const className = cn(
    "flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors",
    isActive ? "bg-brand-blue-light/50 dark:bg-brand-blue-light/10" : "hover:bg-muted/60"
  );

  if (item.href && item.type !== "recent" && item.type !== "popular") {
    return (
      <li>
        <Link
          href={item.href as Route}
          role="option"
          aria-selected={isActive}
          className={className}
          onMouseDown={(event) => event.preventDefault()}
          onClick={onSelect}
        >
          {content}
        </Link>
      </li>
    );
  }

  return (
    <li>
      <button
        type="button"
        role="option"
        aria-selected={isActive}
        className={className}
        onMouseDown={(event) => event.preventDefault()}
        onClick={onSelect}
      >
        {content}
      </button>
    </li>
  );
}

function SearchDropdown({
  id,
  query,
  isLoading,
  results,
  recentSearches,
  popularSearches,
  flatItems,
  activeIndex,
  hasQuery,
  showNoResults,
  onSelectItem,
  onSelectQuery,
  onClearRecent,
  className,
}: SearchDropdownProps) {
  if (hasQuery && isLoading) {
    return (
      <div
        id={id}
        role="listbox"
        className={cn(
          "absolute left-0 right-0 top-[calc(100%+0.5rem)] z-dropdown overflow-hidden rounded-xl border border-border bg-popover shadow-lg",
          className
        )}
      >
        <div className="flex items-center justify-center gap-3 px-4 py-8">
          <Spinner />
          <p className="text-sm text-muted-foreground">Searching products…</p>
        </div>
      </div>
    );
  }

  if (showNoResults) {
    return (
      <div
        id={id}
        role="listbox"
        className={cn(
          "absolute left-0 right-0 top-[calc(100%+0.5rem)] z-dropdown overflow-hidden rounded-xl border border-border bg-popover shadow-lg",
          className
        )}
      >
        <div className="px-4 py-8 text-center">
          <Search className="mx-auto size-8 text-muted-foreground" aria-hidden />
          <p className="mt-3 text-sm font-medium text-foreground">No results found</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Try a product name, SKU, brand, or category like &quot;Cisco&quot; or
            &quot;Networking&quot;.
          </p>
        </div>
      </div>
    );
  }

  if (!hasQuery) {
    return (
      <div
        id={id}
        role="listbox"
        className={cn(
          "absolute left-0 right-0 top-[calc(100%+0.5rem)] z-dropdown max-h-[min(70vh,28rem)] overflow-y-auto rounded-xl border border-border bg-popover shadow-lg sm:max-h-[min(70vh,32rem)]",
          className
        )}
      >
        {recentSearches.length > 0 ? (
          <SearchDropdownSection
            title="Recent searches"
            icon={Clock}
            action={
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="h-7 px-2 text-xs text-muted-foreground"
                onMouseDown={(event) => event.preventDefault()}
                onClick={onClearRecent}
              >
                Clear
              </Button>
            }
          >
            {recentSearches.map((recent) => {
              const item: SearchDropdownItem = {
                type: "recent",
                id: `recent-${recent}`,
                label: recent,
                query: recent,
              };
              const index = getFlatIndex(flatItems, "recent", item.id);
              return (
                <SearchDropdownRow
                  key={item.id}
                  item={item}
                  query=""
                  isActive={activeIndex === index}
                  onSelect={() => onSelectQuery(recent)}
                />
              );
            })}
          </SearchDropdownSection>
        ) : null}

        <SearchDropdownSection title="Popular searches" icon={TrendingUp}>
          {popularSearches.map((popular) => {
            const item: SearchDropdownItem = {
              type: "popular",
              id: `popular-${popular}`,
              label: popular,
              query: popular,
            };
            const index = getFlatIndex(flatItems, "popular", item.id);
            return (
              <SearchDropdownRow
                key={item.id}
                item={item}
                query=""
                isActive={activeIndex === index}
                onSelect={() => onSelectQuery(popular)}
              />
            );
          })}
        </SearchDropdownSection>
      </div>
    );
  }

  return (
    <div
      id={id}
      role="listbox"
      className={cn(
        "absolute left-0 right-0 top-[calc(100%+0.5rem)] z-dropdown max-h-[min(70vh,32rem)] overflow-y-auto rounded-xl border border-border bg-popover shadow-lg",
        className
      )}
    >
      {results.products.length > 0 ? (
        <SearchDropdownSection title="Products" icon={Package}>
          {results.products.map((product) => {
            const item: SearchDropdownItem = {
              type: "product",
              id: product.id,
              label: product.name,
              href: product.href,
              meta: `${product.brand} · ${product.sku}`,
              imageSrc: product.imageSrc,
              imageAlt: product.imageAlt,
            };
            const index = getFlatIndex(flatItems, "product", product.id);
            return (
              <SearchDropdownRow
                key={product.id}
                item={item}
                query={query}
                isActive={activeIndex === index}
                onSelect={() => onSelectItem(item)}
              />
            );
          })}
        </SearchDropdownSection>
      ) : null}

      {results.categories.length > 0 ? (
        <SearchDropdownSection title="Categories" icon={FolderOpen}>
          {results.categories.map((category) => {
            const item: SearchDropdownItem = {
              type: "category",
              id: category.id,
              label: category.label,
              href: category.href,
              meta: category.description,
            };
            const index = getFlatIndex(flatItems, "category", category.id);
            return (
              <SearchDropdownRow
                key={category.id}
                item={item}
                query={query}
                isActive={activeIndex === index}
                onSelect={() => onSelectItem(item)}
              />
            );
          })}
        </SearchDropdownSection>
      ) : null}

      {results.brands.length > 0 ? (
        <SearchDropdownSection title="Brands" icon={Store}>
          {results.brands.map((brand) => {
            const item: SearchDropdownItem = {
              type: "brand",
              id: brand.id,
              label: brand.label,
              href: brand.href,
              meta: brand.productCount,
            };
            const index = getFlatIndex(flatItems, "brand", brand.id);
            return (
              <SearchDropdownRow
                key={brand.id}
                item={item}
                query={query}
                isActive={activeIndex === index}
                onSelect={() => onSelectItem(item)}
              />
            );
          })}
        </SearchDropdownSection>
      ) : null}
    </div>
  );
}

export { SearchDropdown };
