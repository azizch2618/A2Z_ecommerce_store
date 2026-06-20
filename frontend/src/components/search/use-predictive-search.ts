"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import type { PredictiveSearchResults, SearchDropdownItem } from "@/types/search";
import {
  SEARCH_DEBOUNCE_MS,
  SEARCH_MIN_QUERY_LENGTH,
  buildSearchResultsUrl,
  popularSearches,
} from "@/config/search-data";
import { hasSearchResults, searchPredictiveFromApi } from "@/lib/predictive-search-api";
import {
  addRecentSearch,
  clearRecentSearches,
  getRecentSearches,
} from "@/lib/recent-searches";

function buildFlatItems(
  query: string,
  results: PredictiveSearchResults,
  recentSearches: string[]
): SearchDropdownItem[] {
  const trimmed = query.trim();

  if (trimmed.length < SEARCH_MIN_QUERY_LENGTH) {
    const items: SearchDropdownItem[] = [];

    for (const recent of recentSearches) {
      items.push({
        type: "recent",
        id: `recent-${recent}`,
        label: recent,
        query: recent,
      });
    }

    for (const popular of popularSearches) {
      items.push({
        type: "popular",
        id: `popular-${popular}`,
        label: popular,
        query: popular,
      });
    }

    return items;
  }

  const items: SearchDropdownItem[] = [];

  for (const product of results.products) {
    items.push({
      type: "product",
      id: product.id,
      label: product.name,
      href: product.href,
      meta: product.brand,
      imageSrc: product.imageSrc,
      imageAlt: product.imageAlt,
    });
  }

  for (const category of results.categories) {
    items.push({
      type: "category",
      id: category.id,
      label: category.label,
      href: category.href,
      meta: category.description,
    });
  }

  for (const brand of results.brands) {
    items.push({
      type: "brand",
      id: brand.id,
      label: brand.label,
      href: brand.href,
      meta: brand.productCount,
    });
  }

  return items;
}

export interface UsePredictiveSearchOptions {
  onClose?: () => void;
}

export function usePredictiveSearch({ onClose }: UsePredictiveSearchOptions = {}) {
  const router = useRouter();
  const [query, setQuery] = React.useState("");
  const [isOpen, setIsOpen] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(false);
  const [activeIndex, setActiveIndex] = React.useState(-1);
  const [results, setResults] = React.useState<PredictiveSearchResults>({
    products: [],
    categories: [],
    brands: [],
  });
  const [recentSearches, setRecentSearches] = React.useState<string[]>([]);

  React.useEffect(() => {
    setRecentSearches(getRecentSearches());
  }, []);

  React.useEffect(() => {
    if (!isOpen) {
      setActiveIndex(-1);
      return;
    }

    const trimmed = query.trim();
    if (trimmed.length < SEARCH_MIN_QUERY_LENGTH) {
      setResults({ products: [], categories: [], brands: [] });
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    const timer = window.setTimeout(() => {
      searchPredictiveFromApi(trimmed)
        .then((next) => {
          setResults(next);
          setIsLoading(false);
          setActiveIndex(-1);
        })
        .catch(() => {
          setResults({ products: [], categories: [], brands: [] });
          setIsLoading(false);
        });
    }, SEARCH_DEBOUNCE_MS);

    return () => window.clearTimeout(timer);
  }, [query, isOpen]);

  const flatItems = React.useMemo(
    () => buildFlatItems(query, results, recentSearches),
    [query, results, recentSearches]
  );

  const hasQuery = query.trim().length >= SEARCH_MIN_QUERY_LENGTH;
  const showNoResults = hasQuery && !isLoading && !hasSearchResults(results);

  const submitSearch = React.useCallback(
    (value?: string) => {
      const trimmed = (value ?? query).trim();
      if (!trimmed) return;

      const updated = addRecentSearch(trimmed);
      setRecentSearches(updated);
      setIsOpen(false);
      onClose?.();
      router.push(buildSearchResultsUrl(trimmed));
    },
    [onClose, query, router]
  );

  const selectItem = React.useCallback(
    (item: SearchDropdownItem) => {
      if (item.type === "recent" || item.type === "popular") {
        const nextQuery = item.query ?? item.label;
        setQuery(nextQuery);
        submitSearch(nextQuery);
        return;
      }

      if (item.href) {
        if (query.trim()) {
          const updated = addRecentSearch(query.trim());
          setRecentSearches(updated);
        }
        setIsOpen(false);
        onClose?.();
        router.push(item.href);
      }
    },
    [onClose, query, router, submitSearch]
  );

  const handleKeyDown = React.useCallback(
    (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (!isOpen) {
        if (event.key === "ArrowDown") {
          setIsOpen(true);
        }
        return;
      }

      if (event.key === "ArrowDown") {
        event.preventDefault();
        if (flatItems.length === 0) return;
        setActiveIndex((current) => (current + 1) % flatItems.length);
        return;
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();
        if (flatItems.length === 0) return;
        setActiveIndex((current) =>
          current <= 0 ? flatItems.length - 1 : current - 1
        );
        return;
      }

      if (event.key === "Enter") {
        event.preventDefault();
        if (activeIndex >= 0 && flatItems[activeIndex]) {
          selectItem(flatItems[activeIndex]);
          return;
        }
        submitSearch();
        return;
      }

      if (event.key === "Escape") {
        event.preventDefault();
        setIsOpen(false);
        onClose?.();
      }
    },
    [activeIndex, flatItems, isOpen, onClose, selectItem, submitSearch]
  );

  const clearRecent = React.useCallback(() => {
    clearRecentSearches();
    setRecentSearches([]);
  }, []);

  return {
    query,
    setQuery,
    isOpen,
    setIsOpen,
    isLoading,
    results,
    recentSearches,
    popularSearches,
    flatItems,
    activeIndex,
    hasQuery,
    showNoResults,
    handleKeyDown,
    submitSearch,
    selectItem,
    clearRecent,
  };
}
