"use client";

import Link from "next/link";
import type { Route } from "next";
import { Eye, Heart, ShoppingCart } from "lucide-react";

import type { ListingProduct } from "@/types/product";
import { getProductImage } from "@/config/visual-assets";
import { brandIdFromLabel } from "@/config/category-page";
import { BrandLogo } from "@/components/product/brand-logo";
import { PlaceholderImage } from "@/components/home/placeholder-image";
import { ProductStockBadge } from "@/components/product/product-stock-badge";
import { ProductRating } from "@/components/product/product-rating";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

export interface ProductCardProps {
  product: ListingProduct;
  layout?: "grid" | "list";
  isWishlisted?: boolean;
  onToggleWishlist?: (productId: string) => void;
  onAddToCart?: (product: ListingProduct) => void;
  onQuickView?: (product: ListingProduct) => void;
  className?: string;
}

function ProductCard({
  product,
  layout = "grid",
  isWishlisted = false,
  onToggleWishlist,
  onAddToCart,
  onQuickView,
  className,
}: ProductCardProps) {
  const isList = layout === "list";
  const canAddToCart = product.stock !== "out_of_stock";
  const brandId = product.brandId ?? brandIdFromLabel(product.brand);

  return (
    <article
      className={cn(
        "group relative flex overflow-hidden rounded-xl border border-border bg-card shadow-sm transition-all duration-300 hover:border-brand-blue/25 hover:shadow-lg",
        isList ? "flex-col sm:flex-row" : "h-full flex-col hover:-translate-y-0.5",
        className
      )}
    >
      <div
        className={cn(
          "relative shrink-0 overflow-hidden bg-neutral-50",
          isList ? "sm:w-52 md:w-60" : "w-full"
        )}
      >
        <Link href={product.href as Route} className="block">
          <PlaceholderImage
            src={product.imageSrc ?? getProductImage(product.name, product.brand).src}
            alt={product.imageAlt ?? getProductImage(product.name, product.brand).alt}
            aspectRatio="square"
            variant="product"
            className={cn("rounded-none transition-transform duration-500 group-hover:scale-[1.02]", isList && "sm:aspect-square sm:h-full")}
          />
        </Link>

        {product.badge ? (
          <Badge
            className={cn(
              "absolute left-3 top-3 z-10 shadow-sm",
              product.badge === "Sale" && "bg-error text-white",
              product.badge === "New" && "bg-brand-blue text-white",
              product.badge === "Bestseller" && "bg-brand-navy text-white"
            )}
          >
            {product.badge}
          </Badge>
        ) : null}

        <div
          className={cn(
            "absolute inset-x-0 bottom-0 flex items-center justify-center gap-2 bg-gradient-to-t from-brand-navy/80 via-brand-navy/40 to-transparent p-3 transition-opacity duration-300",
            "opacity-0 group-hover:opacity-100 group-focus-within:opacity-100",
            isList && "sm:justify-end sm:pr-3"
          )}
        >
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                type="button"
                variant="secondary"
                size="icon-sm"
                className="size-9 border-0 bg-white/95 text-brand-navy shadow-sm hover:bg-white"
                aria-label="Quick view"
                onClick={() => onQuickView?.(product)}
              >
                <Eye className="size-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Quick view</TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                type="button"
                variant="secondary"
                size="icon-sm"
                className={cn(
                  "size-9 border-0 bg-white/95 shadow-sm hover:bg-white",
                  isWishlisted ? "text-error" : "text-brand-navy"
                )}
                aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
                aria-pressed={isWishlisted}
                onClick={() => onToggleWishlist?.(product.id)}
              >
                <Heart className={cn("size-4", isWishlisted && "fill-current")} />
              </Button>
            </TooltipTrigger>
            <TooltipContent>
              {isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
            </TooltipContent>
          </Tooltip>
        </div>
      </div>

      <div className={cn("flex min-w-0 flex-1 flex-col", isList ? "p-4 md:p-5" : "p-4 md:p-5")}>
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <BrandLogo brandId={brandId} brandName={product.brand} size="xs" />
              <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                {product.brand}
              </p>
            </div>
            <Link href={product.href as Route}>
              <h3 className="mt-1 line-clamp-2 text-sm font-semibold leading-snug text-brand-navy transition-colors hover:text-brand-blue md:text-base">
                {product.name}
              </h3>
            </Link>
          </div>

          {!isList ? (
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              className={cn(
                "shrink-0 text-muted-foreground hover:text-error lg:opacity-0 lg:group-hover:opacity-100",
                isWishlisted && "text-error opacity-100"
              )}
              aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
              aria-pressed={isWishlisted}
              onClick={() => onToggleWishlist?.(product.id)}
            >
              <Heart className={cn("size-4", isWishlisted && "fill-current")} />
            </Button>
          ) : null}
        </div>

        <p className="mt-2 font-mono text-[11px] text-muted-foreground">
          {product.sku}
        </p>

        {product.rating !== undefined ? (
          <ProductRating
            rating={product.rating}
            reviewCount={product.reviewCount}
            size="sm"
            className="mt-2"
          />
        ) : null}

        <div className={cn("mt-4 flex flex-wrap items-end justify-between gap-3", isList && "sm:mt-auto")}>
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-lg font-bold tracking-tight text-brand-navy md:text-xl">
                {product.price}
              </p>
              <Badge
                variant="outline"
                className="h-5 border-brand-blue/25 bg-brand-blue-light/40 px-1.5 text-[10px] font-semibold uppercase tracking-wide text-brand-blue"
              >
                GST incl.
              </Badge>
            </div>
            {product.tradePrice ? (
              <p className="flex items-center gap-1.5 text-sm font-semibold text-brand-blue">
                <Badge variant="trade" className="text-[10px] uppercase">
                  Trade
                </Badge>
                {product.tradePrice}
              </p>
            ) : null}
          </div>

          <ProductStockBadge status={product.stock} size="sm" />
        </div>

        <div
          className={cn(
            "mt-4 flex gap-2",
            isList ? "flex-col sm:flex-row sm:items-center" : "flex-col"
          )}
        >
          <Button
            type="button"
            className="flex-1 gap-2"
            size="sm"
            disabled={!canAddToCart}
            onClick={() => onAddToCart?.(product)}
          >
            <ShoppingCart className="size-4" />
            {product.stock === "back_order" ? "Back order" : "Add to cart"}
          </Button>

          {isList ? (
            <div className="flex gap-2 sm:shrink-0">
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="gap-2"
                onClick={() => onQuickView?.(product)}
              >
                <Eye className="size-4" />
                Quick view
              </Button>
              <Button
                type="button"
                variant="outline"
                size="icon-sm"
                className={cn(isWishlisted && "border-error/30 text-error")}
                aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
                aria-pressed={isWishlisted}
                onClick={() => onToggleWishlist?.(product.id)}
              >
                <Heart className={cn("size-4", isWishlisted && "fill-current")} />
              </Button>
            </div>
          ) : (
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="gap-2 lg:hidden"
              onClick={() => onQuickView?.(product)}
            >
              <Eye className="size-4" />
              Quick view
            </Button>
          )}
        </div>
      </div>
    </article>
  );
}

export { ProductCard };
