"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";

import { Section } from "@/components/layout/section";
import { SectionHeader } from "@/components/home/section-header";
import { ProductCard } from "@/components/product/product-card";
import { useProducts } from "@/lib/api/hooks/use-products";
import { mapApiProductToListing } from "@/lib/api/mappers/product-mapper";

function FeaturedProductsSection() {
  const { data, isLoading, isError } = useProducts({
    sort: "featured",
    limit: 8,
  });

  const products = React.useMemo(
    () => (data?.data ?? []).map(mapApiProductToListing),
    [data]
  );

  return (
    <Section variant="subtle" className="relative overflow-hidden">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(0,102,204,0.06),transparent_60%)]"
        aria-hidden
      />
      <div className="relative">
        <SectionHeader
          eyebrow="Top sellers"
          title="Featured products"
          description="Popular picks from networking, tools, and security — in stock and ready to ship Australia-wide."
          href="/products"
          linkLabel="View all products"
        />

        {isLoading ? (
          <div className="flex min-h-[200px] items-center justify-center">
            <Loader2 className="size-8 animate-spin text-brand-blue" />
          </div>
        ) : isError ? (
          <p className="text-center text-sm text-muted-foreground">
            Could not load featured products.
          </p>
        ) : (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 md:gap-6 lg:grid-cols-4">
            {products.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </Section>
  );
}

export { FeaturedProductsSection };
