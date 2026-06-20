"use client";

import Link from "next/link";
import type { Route } from "next";
import { ExternalLink, ShoppingCart, X } from "lucide-react";

import type { CompareProduct } from "@/types/compare";
import { useCompare } from "@/components/compare/compare-provider";
import { Button } from "@/components/ui/button";

export interface CompareProductActionsProps {
  product: CompareProduct;
  layout?: "stacked" | "inline";
  className?: string;
}

function CompareProductActions({
  product,
  layout = "stacked",
  className,
}: CompareProductActionsProps) {
  const { addToCart, removeProduct } = useCompare();
  const canAddToCart = product.stock !== "out_of_stock";

  return (
    <div
      className={
        layout === "inline"
          ? `flex flex-wrap gap-2 ${className ?? ""}`
          : `flex flex-col gap-2 ${className ?? ""}`
      }
    >
      <Button
        type="button"
        size="sm"
        className="w-full gap-2"
        disabled={!canAddToCart}
        onClick={() => addToCart(product.id)}
      >
        <ShoppingCart className="size-4" />
        Add to cart
      </Button>
      <div className={layout === "inline" ? "flex gap-2" : "grid grid-cols-2 gap-2"}>
        <Button asChild variant="outline" size="sm" className="gap-1.5">
          <Link href={product.href as Route}>
            <ExternalLink className="size-3.5" />
            View
          </Link>
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="gap-1.5 text-muted-foreground hover:text-error"
          onClick={() => removeProduct(product.id)}
        >
          <X className="size-3.5" />
          Remove
        </Button>
      </div>
    </div>
  );
}

export { CompareProductActions };
