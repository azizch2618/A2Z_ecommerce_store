"use client";

import Link from "next/link";
import type { Route } from "next";
import { ArrowUpRight } from "lucide-react";

import type { FeaturedBrand } from "@/config/category-page";
import { getBrandImage } from "@/config/visual-assets";
import { PlaceholderImage } from "@/components/home/placeholder-image";
import { Container } from "@/components/layout/container";
import { cn } from "@/lib/utils";

export interface CategoryFeaturedBrandsProps {
  brands: FeaturedBrand[];
  onBrandSelect?: (brandId: string) => void;
  activeBrandIds?: string[];
  className?: string;
}

function BrandCard({
  brand,
  isActive,
  onBrandSelect,
}: {
  brand: FeaturedBrand;
  isActive: boolean;
  onBrandSelect?: (brandId: string) => void;
}) {
  const cardClassName = cn(
    "group min-w-[10.5rem] flex-shrink-0 rounded-xl border bg-card p-3 text-left shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:border-brand-blue/30 hover:shadow-md md:min-w-0",
    isActive ? "border-brand-blue ring-2 ring-brand-blue/20" : "border-border"
  );

  const content = (
    <>
      <div className="mb-3 overflow-hidden rounded-lg">
        <PlaceholderImage
          src={getBrandImage(brand.filterBrandId).src}
          alt={getBrandImage(brand.filterBrandId).alt}
          aspectRatio="brand"
          variant="brand"
          className="transition-transform duration-500 group-hover:scale-105"
        />
      </div>
      <div className="flex items-start justify-between gap-1">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-brand-navy group-hover:text-brand-blue">
            {brand.name}
          </p>
          <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">
            {brand.description}
          </p>
          <p className="mt-1 text-[10px] font-medium uppercase tracking-wide text-brand-blue">
            {brand.productCount}
          </p>
        </div>
        <ArrowUpRight className="size-3.5 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
      </div>
    </>
  );

  if (onBrandSelect) {
    return (
      <button
        type="button"
        onClick={() => onBrandSelect(brand.filterBrandId)}
        className={cardClassName}
      >
        {content}
      </button>
    );
  }

  return (
    <Link href={brand.href as Route} className={cardClassName}>
      {content}
    </Link>
  );
}

function CategoryFeaturedBrands({
  brands,
  onBrandSelect,
  activeBrandIds = [],
  className,
}: CategoryFeaturedBrandsProps) {
  return (
    <section
      className={cn("border-b border-border bg-surface-subtle py-8 md:py-10", className)}
      aria-labelledby="featured-brands-heading"
    >
      <Container>
        <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-brand-blue">
              Authorised stock
            </p>
            <h2
              id="featured-brands-heading"
              className="mt-1 text-xl font-bold text-brand-navy md:text-2xl"
            >
              Featured brands
            </h2>
          </div>
          <Link
            href="/brands"
            className="text-sm font-medium text-brand-blue hover:underline"
          >
            View all brands
          </Link>
        </div>

        <div className="flex gap-3 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:none] md:grid md:grid-cols-3 md:overflow-visible lg:grid-cols-6 [&::-webkit-scrollbar]:hidden">
          {brands.map((brand) => (
            <BrandCard
              key={brand.id}
              brand={brand}
              isActive={activeBrandIds.includes(brand.filterBrandId)}
              onBrandSelect={onBrandSelect}
            />
          ))}
        </div>
      </Container>
    </section>
  );
}

export { CategoryFeaturedBrands };
