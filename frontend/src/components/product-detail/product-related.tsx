"use client";

import type { CategoryProduct } from "@/config/category-page";
import { ProductListingGrid } from "@/components/product";
import { cn } from "@/lib/utils";

export interface ProductRelatedProps {
  products: CategoryProduct[];
  className?: string;
}

function ProductRelated({ products, className }: ProductRelatedProps) {
  if (products.length === 0) return null;

  return (
    <div className={cn(className)}>
      <ProductListingGrid products={products} layout="grid" />
    </div>
  );
}

export { ProductRelated };
