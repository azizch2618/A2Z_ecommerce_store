import Link from "next/link";
import { ShoppingCart } from "lucide-react";

import type { ProductPlaceholder } from "@/config/homepage";
import { getProductImage } from "@/config/visual-assets";
import { PlaceholderImage } from "@/components/home/placeholder-image";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export interface ProductCardWireframeProps {
  product: ProductPlaceholder;
  className?: string;
}

const stockLabels = {
  in_stock: {
    label: "In stock",
    className: "text-success bg-success-light",
  },
  low_stock: {
    label: "Low stock",
    className: "text-warning bg-warning-light",
  },
  out_of_stock: {
    label: "Out of stock",
    className: "text-error bg-error-light",
  },
};

function ProductCardWireframe({ product, className }: ProductCardWireframeProps) {
  const stock = stockLabels[product.stock];
  const image = getProductImage(product.name, product.brand);

  return (
    <article
      className={cn(
        "group flex h-full flex-col overflow-hidden rounded-xl border border-border bg-card shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-brand-blue/20 hover:shadow-lg",
        className
      )}
    >
      <Link href={product.href} className="relative block overflow-hidden">
        <PlaceholderImage
          src={image.src}
          alt={image.alt}
          aspectRatio="square"
          variant="product"
          className="rounded-none transition-transform duration-500 group-hover:scale-[1.03]"
        />
        {product.badge ? (
          <Badge
            className={cn(
              "absolute left-3 top-3 shadow-sm",
              product.badge === "Sale" && "bg-error text-white",
              product.badge === "New" && "bg-brand-blue text-white"
            )}
          >
            {product.badge}
          </Badge>
        ) : null}
      </Link>

      <div className="flex flex-1 flex-col p-4 md:p-5">
        <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
          {product.brand}
        </p>
        <Link href={product.href}>
          <h3 className="mt-1.5 line-clamp-2 text-sm font-semibold leading-snug text-brand-navy transition-colors group-hover:text-brand-blue md:text-base">
            {product.name}
          </h3>
        </Link>
        <p className="mt-1.5 font-mono text-[11px] text-muted-foreground">
          {product.sku}
        </p>

        <div className="mt-4 space-y-1 border-t border-border pt-4">
          <p className="text-lg font-bold tracking-tight text-brand-navy md:text-xl">
            {product.price}
            <span className="ml-1.5 text-xs font-normal text-muted-foreground">
              inc. GST
            </span>
          </p>
          {product.tradePrice ? (
            <p className="inline-flex items-center gap-1.5 text-sm font-semibold text-brand-blue">
              <span className="rounded bg-brand-blue-light px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-brand-blue">
                Trade
              </span>
              {product.tradePrice}
            </p>
          ) : null}
        </div>

        <div className="mt-3 flex items-center justify-between gap-2">
          <span
            className={cn(
              "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium",
              stock.className
            )}
          >
            <span className="size-1.5 rounded-full bg-current" />
            {stock.label}
          </span>
        </div>

        <Button
          className="mt-4 w-full gap-2"
          size="sm"
          disabled={product.stock === "out_of_stock"}
        >
          <ShoppingCart className="size-4" />
          Add to cart
        </Button>
      </div>
    </article>
  );
}

export { ProductCardWireframe };
