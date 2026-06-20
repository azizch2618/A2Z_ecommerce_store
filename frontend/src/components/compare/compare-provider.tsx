"use client";

import * as React from "react";
import { toast } from "sonner";

import { MAX_COMPARE_PRODUCTS } from "@/config/compare";
import type { CompareProduct } from "@/types/compare";
import { compareProducts } from "@/lib/api/services/products.service";
import { mapApiProductToCompareProduct } from "@/lib/api/mappers/compare-mapper";

const STORAGE_KEY = "a2z_compare_ids";

interface CompareContextValue {
  products: CompareProduct[];
  count: number;
  canCompare: boolean;
  isAtMax: boolean;
  isLoading: boolean;
  removeProduct: (id: string) => void;
  addProduct: (product: CompareProduct) => boolean;
  isInCompare: (id: string) => boolean;
  addToCart: (id: string) => void;
  refreshProducts: () => Promise<void>;
}

const CompareContext = React.createContext<CompareContextValue | null>(null);

function readStoredIds(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as string[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeStoredIds(ids: string[]) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
}

function CompareProvider({ children }: { children: React.ReactNode }) {
  const [productIds, setProductIds] = React.useState<string[]>([]);
  const [products, setProducts] = React.useState<CompareProduct[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);

  const loadProducts = React.useCallback(async (ids: string[]) => {
    if (ids.length === 0) {
      setProducts([]);
      return;
    }
    setIsLoading(true);
    try {
      const response = await compareProducts(ids);
      setProducts(response.products.map(mapApiProductToCompareProduct));
    } catch {
      setProducts([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  React.useEffect(() => {
    const ids = readStoredIds();
    setProductIds(ids);
    void loadProducts(ids);
  }, [loadProducts]);

  const removeProduct = React.useCallback(
    (id: string) => {
      setProductIds((current) => {
        const next = current.filter((entry) => entry !== id);
        writeStoredIds(next);
        void loadProducts(next);
        return next;
      });
      const removed = products.find((item) => item.id === id);
      if (removed) {
        toast.info(`${removed.name} removed from compare`);
      }
    },
    [loadProducts, products]
  );

  const addProduct = React.useCallback(
    (product: CompareProduct) => {
      if (productIds.includes(product.id)) {
        return false;
      }
      if (productIds.length >= MAX_COMPARE_PRODUCTS) {
        toast.error(`Compare up to ${MAX_COMPARE_PRODUCTS} products at a time`);
        return false;
      }
      const next = [...productIds, product.id];
      setProductIds(next);
      writeStoredIds(next);
      void loadProducts(next);
      toast.success(`${product.name} added to compare`);
      return true;
    },
    [loadProducts, productIds]
  );

  const isInCompare = React.useCallback(
    (id: string) => productIds.includes(id),
    [productIds]
  );

  const addToCart = React.useCallback(
    (id: string) => {
      const product = products.find((item) => item.id === id);
      if (!product) return;
      if (product.stock === "out_of_stock") {
        toast.error("This item is out of stock");
        return;
      }
      toast.info("Open the product page to add this item to cart");
    },
    [products]
  );

  const value = React.useMemo(
    () => ({
      products,
      count: products.length,
      canCompare: products.length >= 2,
      isAtMax: productIds.length >= MAX_COMPARE_PRODUCTS,
      isLoading,
      removeProduct,
      addProduct,
      isInCompare,
      addToCart,
      refreshProducts: async () => loadProducts(productIds),
    }),
    [
      products,
      productIds.length,
      isLoading,
      removeProduct,
      addProduct,
      isInCompare,
      addToCart,
      loadProducts,
      productIds,
    ]
  );

  return <CompareContext.Provider value={value}>{children}</CompareContext.Provider>;
}

function useCompare() {
  const context = React.useContext(CompareContext);
  if (!context) {
    throw new Error("useCompare must be used within CompareProvider");
  }
  return context;
}

export { CompareProvider, useCompare };
