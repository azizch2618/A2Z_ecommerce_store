"use client";

import { Minus, Plus, ShoppingCart } from "lucide-react";

import type { ProductDetail } from "@/config/product-detail";
import { ProductStockBadge } from "@/components/product/product-stock-badge";
import { Button } from "@/components/ui/button";

export interface ProductMobileBarProps {
  product: ProductDetail;
  quantity: number;
  onQuantityChange: (quantity: number) => void;
  maxQuantity?: number;
  onAddToCart: () => void;
}

function ProductMobileBar({
  product,
  quantity,
  onQuantityChange,
  maxQuantity = 99,
  onAddToCart,
}: ProductMobileBarProps) {
  const canAddToCart = product.stock !== "out_of_stock";

  return (
    <div className="fixed inset-x-0 bottom-14 z-sticky border-t border-border bg-background/95 shadow-lg backdrop-blur-md lg:hidden">
      <div className="container-app flex items-center gap-3 p-3">
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-bold text-brand-navy">{product.price}</p>
          <div className="mt-0.5 flex items-center gap-2">
            <p className="text-[10px] text-muted-foreground">GST included</p>
            <ProductStockBadge status={product.stock} size="sm" />
          </div>
        </div>

        <div className="flex items-center rounded-lg border border-border">
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="size-8 rounded-none"
            onClick={() => onQuantityChange(Math.max(1, quantity - 1))}
            disabled={!canAddToCart || quantity <= 1}
            aria-label="Decrease quantity"
          >
            <Minus className="size-3.5" />
          </Button>
          <span className="w-8 text-center text-sm font-semibold tabular-nums">
            {quantity}
          </span>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="size-8 rounded-none"
            onClick={() => onQuantityChange(Math.min(maxQuantity, quantity + 1))}
            disabled={!canAddToCart || quantity >= maxQuantity}
            aria-label="Increase quantity"
          >
            <Plus className="size-3.5" />
          </Button>
        </div>

        <Button
          type="button"
          className="shrink-0 gap-2"
          disabled={!canAddToCart}
          onClick={onAddToCart}
        >
          <ShoppingCart className="size-4" />
          Add to cart
        </Button>
      </div>
    </div>
  );
}

export { ProductMobileBar };
