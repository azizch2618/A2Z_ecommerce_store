"use client";

import * as React from "react";
import Link from "next/link";
import type { Route } from "next";
import {
  FileText,
  Heart,
  Package,
  ShoppingCart,
  Shield,
  Truck,
} from "lucide-react";

import type { ProductDetail } from "@/config/product-detail";
import { brandIdFromLabel } from "@/config/category-page";
import { BulkQuoteDialog } from "@/components/product-detail/bulk-quote-dialog";
import { ProductGstPricing } from "@/components/product-detail/product-gst-pricing";
import { QuantitySelector } from "@/components/product-detail/quantity-selector";
import { useWishlist } from "@/components/wishlist";
import { BrandLogo } from "@/components/product/brand-logo";
import { ProductRating } from "@/components/product/product-rating";
import { ProductStockBadge } from "@/components/product/product-stock-badge";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

function parseAudPrice(value?: string): number | undefined {
  if (!value) return undefined;
  const parsed = Number.parseFloat(value.replace(/[^0-9.]/g, ""));
  return Number.isFinite(parsed) ? parsed : undefined;
}

export interface ProductPurchasePanelProps {
  product: ProductDetail;
  quantity: number;
  onQuantityChange: (quantity: number) => void;
  maxQuantity?: number;
  onAddToCart: () => void;
  onReviewsClick?: () => void;
  className?: string;
}

function ProductPurchasePanel({
  product,
  quantity,
  onQuantityChange,
  maxQuantity = 99,
  onAddToCart,
  onReviewsClick,
  className,
}: ProductPurchasePanelProps) {
  const { isWishlisted, toggleFromDetail } = useWishlist();
  const [quoteOpen, setQuoteOpen] = React.useState(false);

  const canAddToCart = product.stock !== "out_of_stock";
  const tradePriceValue = parseAudPrice(product.tradePrice);
  const wishlisted = isWishlisted(product.id);

  const handleWishlist = () => {
    toggleFromDetail(product);
  };

  return (
    <>
      <div className={cn("space-y-6", className)}>
        <div className="space-y-3">
          {product.badge ? (
            <Badge
              className={cn(
                product.badge === "Sale" && "bg-error text-white",
                product.badge === "New" && "bg-brand-blue text-white",
                product.badge === "Bestseller" && "bg-brand-navy text-white"
              )}
            >
              {product.badge}
            </Badge>
          ) : null}

          <div className="flex items-center gap-2.5">
            <BrandLogo
              brandId={brandIdFromLabel(product.brand)}
              brandName={product.brand}
              size="md"
            />
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              <Link
                href={product.brandHref as Route}
                className="transition-colors hover:text-brand-blue"
              >
                {product.brand}
              </Link>
            </p>
          </div>

          <h1 className="text-2xl font-bold leading-tight tracking-tight text-brand-navy md:text-3xl lg:text-[2rem] lg:leading-tight">
            {product.name}
          </h1>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-muted-foreground">
            <p>
              SKU:{" "}
              <span className="font-mono font-medium text-foreground">
                {product.sku}
              </span>
            </p>
            <span className="hidden text-border sm:inline" aria-hidden>
              |
            </span>
            <p>
              Category:{" "}
              <Link
                href={product.categoryHref as Route}
                className="font-medium text-brand-blue hover:underline"
              >
                {product.category}
              </Link>
            </p>
          </div>

          {product.rating !== undefined ? (
            <button
              type="button"
              onClick={onReviewsClick}
              className={cn(
                "pt-1 text-left",
                onReviewsClick && "cursor-pointer transition-opacity hover:opacity-80"
              )}
              disabled={!onReviewsClick}
            >
              <ProductRating
                rating={product.rating}
                reviewCount={product.reviewCount}
              />
            </button>
          ) : null}
        </div>

        <p className="text-base leading-relaxed text-muted-foreground">
          {product.shortDescription}
        </p>

        <div className="rounded-xl border border-border bg-neutral-50/80 p-5 md:p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex flex-wrap items-baseline gap-2">
                <p className="text-3xl font-bold tracking-tight text-brand-navy">
                  {product.price}
                </p>
                <Badge
                  variant="outline"
                  className="border-brand-blue/30 bg-brand-blue-light/50 text-[11px] font-semibold uppercase tracking-wide text-brand-blue"
                >
                  GST included
                </Badge>
              </div>
              {product.tradePrice ? (
                <p className="flex flex-wrap items-center gap-2 text-base font-semibold text-brand-blue">
                  <Badge variant="trade" className="text-[10px] uppercase">
                    Trade
                  </Badge>
                  {product.tradePrice}
                  <span className="text-sm font-normal text-muted-foreground">
                    inc. GST
                  </span>
                  <Link
                    href="/trade"
                    className="text-sm font-medium underline-offset-2 hover:underline"
                  >
                    Open trade account
                  </Link>
                </p>
              ) : null}
              <p className="text-xs text-muted-foreground">
                All prices include 10% GST. Tax invoice provided on every order.
              </p>
              <ProductGstPricing
                className="mt-4"
                priceValue={product.priceValue}
                tradePriceValue={tradePriceValue}
                quantity={quantity}
              />
            </div>

            <div className="space-y-2 sm:text-right">
              <ProductStockBadge status={product.stock} />
              {product.stockCount !== undefined && product.stock !== "out_of_stock" ? (
                <p className="text-xs text-muted-foreground">
                  {product.stockCount} units in Sydney warehouse
                </p>
              ) : null}
            </div>
          </div>

          <div className="mt-6 space-y-4 border-t border-border pt-6">
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
                <div className="space-y-1.5">
                  <label className="text-sm font-medium text-brand-navy">
                    Quantity
                  </label>
                  <QuantitySelector
                    value={quantity}
                    onChange={onQuantityChange}
                    max={maxQuantity}
                    disabled={!canAddToCart}
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2 sm:flex-row">
                <Button
                  type="button"
                  size="lg"
                  className="flex-1 gap-2"
                  disabled={!canAddToCart}
                  onClick={onAddToCart}
                >
                  <ShoppingCart className="size-5" />
                  {product.stock === "back_order" ? "Back order" : "Add to cart"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  size="lg"
                  className={cn(
                    "gap-2",
                    wishlisted &&
                      "border-error/30 bg-error-light text-error hover:bg-error-light"
                  )}
                  aria-pressed={wishlisted}
                  onClick={handleWishlist}
                >
                  <Heart className={cn("size-5", wishlisted && "fill-current")} />
                  {wishlisted ? "Saved" : "Wishlist"}
                </Button>
              </div>

              <Button
                type="button"
                variant="secondary"
                size="lg"
                className="w-full gap-2"
                onClick={() => setQuoteOpen(true)}
              >
                <FileText className="size-4" />
                Request bulk quote
              </Button>
            </div>
          </div>
        </div>

        <ul className="grid gap-3 sm:grid-cols-2">
          <li className="flex items-start gap-3 rounded-lg border border-border bg-card p-3 text-sm">
            <Truck className="mt-0.5 size-4 shrink-0 text-brand-blue" />
            <div>
              <p className="font-medium text-brand-navy">Delivery</p>
              <p className="text-muted-foreground">{product.deliveryNote}</p>
            </div>
          </li>
          <li className="flex items-start gap-3 rounded-lg border border-border bg-card p-3 text-sm">
            <Shield className="mt-0.5 size-4 shrink-0 text-brand-blue" />
            <div>
              <p className="font-medium text-brand-navy">Warranty</p>
              <p className="text-muted-foreground">{product.warranty}</p>
            </div>
          </li>
          <li className="flex items-start gap-3 rounded-lg border border-border bg-card p-3 text-sm sm:col-span-2">
            <Package className="mt-0.5 size-4 shrink-0 text-brand-blue" />
            <div>
              <p className="font-medium text-brand-navy">Volume orders</p>
              <p className="text-muted-foreground">
                Ordering 10+ units? Use{" "}
                <button
                  type="button"
                  className="font-medium text-brand-blue hover:underline"
                  onClick={() => setQuoteOpen(true)}
                >
                  Request bulk quote
                </button>{" "}
                for project pricing and staged delivery.
              </p>
            </div>
          </li>
        </ul>
      </div>

      <BulkQuoteDialog
        product={product}
        open={quoteOpen}
        onOpenChange={setQuoteOpen}
        defaultQuantity={Math.max(10, quantity)}
      />
    </>
  );
}

export { ProductPurchasePanel };
