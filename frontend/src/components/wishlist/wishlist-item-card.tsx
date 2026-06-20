"use client";

import Link from "next/link";
import type { Route } from "next";
import { ExternalLink, ShoppingCart, Trash2 } from "lucide-react";
import { toast } from "sonner";

import type { WishlistItem } from "@/types/wishlist";
import { formatAud } from "@/lib/cart";
import { useWishlist } from "@/components/wishlist/wishlist-provider";
import { ProductStockBadge } from "@/components/product/product-stock-badge";
import { RemoteImage } from "@/components/ui/remote-image";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";

export interface WishlistItemCardProps {
  item: WishlistItem;
  className?: string;
}

function WishlistItemCard({ item, className }: WishlistItemCardProps) {
  const { moveToCart, removeItem } = useWishlist();
  const hasTradePrice =
    item.tradePriceIncGst !== undefined && item.tradePriceIncGst < item.priceIncGst;
  const canMoveToCart = item.stock !== "out_of_stock";

  return (
    <Card className={cn("flex h-full flex-col overflow-hidden", className)}>
      <CardHeader className="relative p-0">
        <Link
          href={item.href as Route}
          className="relative block aspect-[4/3] overflow-hidden bg-muted"
        >
          <RemoteImage
            src={item.imageSrc}
            alt={item.imageAlt}
            fill
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            className="object-cover transition-transform duration-300 hover:scale-105"
          />
        </Link>
        {hasTradePrice ? (
          <Badge className="absolute left-3 top-3 bg-brand-blue text-white hover:bg-brand-blue">
            Trade price
          </Badge>
        ) : null}
      </CardHeader>

      <CardContent className="flex flex-1 flex-col gap-3 p-4">
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
            {item.brand}
          </p>
          <Link href={item.href as Route}>
            <h3 className="mt-1 line-clamp-2 text-sm font-semibold text-foreground transition-colors hover:text-brand-blue">
              {item.name}
            </h3>
          </Link>
          <p className="mt-1 font-mono text-[11px] text-muted-foreground">
            SKU: {item.sku}
          </p>
        </div>

        <ProductStockBadge status={item.stock} size="sm" />

        <div className="mt-auto space-y-1">
          <div className="flex flex-wrap items-baseline gap-2">
            <p className="text-lg font-bold tabular-nums text-foreground">
              {formatAud(hasTradePrice ? item.tradePriceIncGst! : item.priceIncGst)}
            </p>
            {hasTradePrice ? (
              <p className="text-sm text-muted-foreground line-through">
                {formatAud(item.priceIncGst)}
              </p>
            ) : null}
          </div>
          {hasTradePrice ? (
            <p className="text-xs text-brand-blue">
              Trade {formatAud(item.tradePriceIncGst!)} · Retail{" "}
              {formatAud(item.priceIncGst)}
            </p>
          ) : (
            <p className="text-xs text-muted-foreground">GST included</p>
          )}
        </div>
      </CardContent>

      <CardFooter className="flex flex-col gap-2 border-t border-border p-4">
        <Button
          type="button"
          className="w-full gap-2"
          disabled={!canMoveToCart}
          onClick={() => moveToCart(item.id)}
        >
          <ShoppingCart className="size-4" />
          Move to cart
        </Button>
        <div className="grid w-full grid-cols-2 gap-2">
          <Button asChild variant="outline" size="sm" className="gap-1.5">
            <Link href={item.href as Route}>
              <ExternalLink className="size-3.5" />
              View
            </Link>
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="gap-1.5 text-muted-foreground hover:text-error"
            onClick={() => {
              removeItem(item.id);
              toast.info(`${item.name} removed from wishlist`);
            }}
          >
            <Trash2 className="size-3.5" />
            Remove
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}

export { WishlistItemCard };
