"use client";

import * as React from "react";

import { useProducts } from "@/lib/api/hooks/use-products";
import type { ProductListParams } from "@/lib/api/types/product";

export function useCursorProductListing(
  baseParams: Omit<ProductListParams, "cursor">,
  resetKey: string
) {
  const [currentPage, setCurrentPage] = React.useState(1);
  const [cursors, setCursors] = React.useState<Record<number, string | null>>({
    1: null,
  });
  const [maxPage, setMaxPage] = React.useState(1);

  React.useEffect(() => {
    setCurrentPage(1);
    setCursors({ 1: null });
    setMaxPage(1);
  }, [resetKey]);

  const cursor = cursors[currentPage] ?? null;

  const query = useProducts({
    ...baseParams,
    cursor: cursor ?? undefined,
  });

  React.useEffect(() => {
    const nextCursor = query.data?.pagination.next_cursor;
    if (nextCursor) {
      setCursors((current) => ({
        ...current,
        [currentPage + 1]: nextCursor,
      }));
    }
    if (query.data?.pagination.has_more) {
      setMaxPage((current) => Math.max(current, currentPage + 1));
    } else {
      setMaxPage(currentPage);
    }
  }, [query.data, currentPage]);

  const goToPage = React.useCallback((page: number) => {
    setCurrentPage(Math.max(1, page));
  }, []);

  return {
    ...query,
    currentPage,
    goToPage,
    maxPage,
    hasMore: query.data?.pagination.has_more ?? false,
  };
}
