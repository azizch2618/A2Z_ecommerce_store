"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";

import { ProductDetailView } from "@/components/product-detail";
import { useProductDetails } from "@/lib/api/hooks/use-products";
import {
  mapApiProductToCategoryProduct,
  mapApiProductToDetail,
} from "@/lib/api/mappers/product-mapper";
import { Button } from "@/components/ui/button";

export interface ProductDetailPageClientProps {
  slug: string;
}

function ProductDetailPageClient({ slug }: ProductDetailPageClientProps) {
  const { data, isLoading, isError, refetch } = useProductDetails(slug);

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-brand-blue" aria-label="Loading product" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 px-4 text-center">
        <p className="text-lg font-medium text-brand-navy">Product not found</p>
        <p className="text-sm text-muted-foreground">
          Ensure the API is running and demo data is seeded.
        </p>
        <Button onClick={() => refetch()}>Retry</Button>
      </div>
    );
  }

  const product = mapApiProductToDetail(data);
  const relatedProducts = data.related_products.map(mapApiProductToCategoryProduct);

  return <ProductDetailView product={product} relatedProducts={relatedProducts} />;
}

export { ProductDetailPageClient };
