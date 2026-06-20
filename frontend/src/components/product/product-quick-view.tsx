"use client";

import Link from "next/link";
import type { Route } from "next";
import { ExternalLink, Heart, ShoppingCart } from "lucide-react";

import type { ListingProduct } from "@/types/product";
import { getProductImage } from "@/config/visual-assets";
import { PlaceholderImage } from "@/components/home/placeholder-image";
import { ProductStockBadge } from "@/components/product/product-stock-badge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { cn } from "@/lib/utils";

export interface ProductQuickViewProps {
  product: ListingProduct | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  isWishlisted?: boolean;
  onToggleWishlist?: (productId: string) => void;
  onAddToCart?: (product: ListingProduct) => void;
}

function ProductQuickView({
  product,
  open,
  onOpenChange,
  isWishlisted = false,
  onToggleWishlist,
  onAddToCart,
}: ProductQuickViewProps) {
  if (!product) return null;

  const canOrder = product.stock !== "out_of_stock";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto p-0 sm:max-w-3xl">
        <div className="grid md:grid-cols-[minmax(0,1fr)_minmax(0,1.1fr)]">
          <div className="relative border-b border-border bg-neutral-50 md:border-b-0 md:border-r">
            <PlaceholderImage
              src={product.imageSrc ?? getProductImage(product.name, product.brand).src}
              alt={product.imageAlt ?? getProductImage(product.name, product.brand).alt}
              aspectRatio="square"
              variant="product"
              className="rounded-none md:min-h-full"
            />
            {product.badge ? (
              <Badge
                className={cn(
                  "absolute left-4 top-4 shadow-sm",
                  product.badge === "Sale" && "bg-error text-white",
                  product.badge === "New" && "bg-brand-blue text-white",
                  product.badge === "Bestseller" && "bg-brand-navy text-white"
                )}
              >
                {product.badge}
              </Badge>
            ) : null}
          </div>

          <div className="flex flex-col p-6 md:p-8">
            <DialogHeader className="space-y-3 text-left">
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                {product.brand}
              </p>
              <DialogTitle className="text-xl font-bold leading-snug text-brand-navy md:text-2xl">
                {product.name}
              </DialogTitle>
              <DialogDescription asChild>
                <p className="font-mono text-xs text-muted-foreground">
                  SKU: {product.sku}
                </p>
              </DialogDescription>
            </DialogHeader>

            <div className="mt-5 flex flex-wrap items-center gap-2">
              <ProductStockBadge status={product.stock} />
              <Badge variant="outline" className="border-brand-blue/30 bg-brand-blue-light/50 text-brand-blue">
                GST included
              </Badge>
            </div>

            <div className="mt-6 space-y-2 border-y border-border py-5">
              <p className="text-2xl font-bold tracking-tight text-brand-navy">
                {product.price}
              </p>
              {product.tradePrice ? (
                <p className="flex items-center gap-2 text-sm font-semibold text-brand-blue">
                  <Badge variant="trade" className="text-[10px] uppercase">
                    Trade
                  </Badge>
                  {product.tradePrice}
                  <span className="font-normal text-muted-foreground">inc. GST</span>
                </p>
              ) : null}
            </div>

            {product.description ? (
              <p className="mt-5 text-sm leading-relaxed text-muted-foreground">
                {product.description}
              </p>
            ) : null}

            {product.highlights && product.highlights.length > 0 ? (
              <ul className="mt-4 space-y-2">
                {product.highlights.map((item) => (
                  <li
                    key={item}
                    className="flex items-start gap-2 text-sm text-foreground"
                  >
                    <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-brand-blue" />
                    {item}
                  </li>
                ))}
              </ul>
            ) : null}

            <div className="mt-auto flex flex-col gap-3 pt-8 sm:flex-row">
              <Button
                type="button"
                className="flex-1 gap-2"
                disabled={!canOrder}
                onClick={() => onAddToCart?.(product)}
              >
                <ShoppingCart className="size-4" />
                {product.stock === "back_order" ? "Back order" : "Add to cart"}
              </Button>
              <Button
                type="button"
                variant="outline"
                size="icon"
                className={cn(
                  "shrink-0",
                  isWishlisted && "border-error/30 bg-error-light text-error hover:bg-error-light"
                )}
                aria-label={isWishlisted ? "Remove from wishlist" : "Add to wishlist"}
                aria-pressed={isWishlisted}
                onClick={() => onToggleWishlist?.(product.id)}
              >
                <Heart className={cn("size-4", isWishlisted && "fill-current")} />
              </Button>
            </div>

            <Button
              asChild
              variant="ghost"
              className="mt-3 w-full gap-2 text-brand-blue"
            >
              <Link href={product.href as Route} onClick={() => onOpenChange(false)}>
                View full product details
                <ExternalLink className="size-3.5" />
              </Link>
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export { ProductQuickView };
