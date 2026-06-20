"use client";

import Link from "next/link";
import type { Route } from "next";
import { Trash2 } from "lucide-react";

import type { CartItem } from "@/types/cart";
import { formatAud } from "@/lib/cart";
import { QuantitySelector } from "@/components/product-detail/quantity-selector";
import { RemoteImage } from "@/components/ui/remote-image";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export interface CartLineItemProps {
  item: CartItem;
  onQuantityChange: (id: string, quantity: number) => void;
  onRemove: (id: string) => void;
  className?: string;
}

function CartLineItem({
  item,
  onQuantityChange,
  onRemove,
  className,
}: CartLineItemProps) {
  const lineTotal = item.priceValue * item.quantity;
  const tradeLineTotal =
    item.tradePriceValue !== undefined
      ? item.tradePriceValue * item.quantity
      : null;
  const hasTradeDiscount =
    tradeLineTotal !== null && tradeLineTotal < lineTotal;

  return (
    <article
      className={cn(
        "grid gap-4 border-b border-border py-5 last:border-b-0 sm:grid-cols-[auto_minmax(0,1fr)_auto] sm:items-center sm:gap-6",
        className
      )}
    >
      <Link
        href={item.href as Route}
        className="relative size-20 shrink-0 overflow-hidden rounded-lg border border-border bg-neutral-50 sm:size-24"
      >
        <RemoteImage
          src={item.imageSrc}
          alt={item.imageAlt}
          fill
          sizes="96px"
          className="object-cover"
        />
      </Link>

      <div className="min-w-0 space-y-2">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-muted-foreground">
              {item.brand}
            </p>
            {hasTradeDiscount ? (
              <Badge
                variant="outline"
                className="border-brand-blue/30 bg-brand-blue-light/40 px-1.5 py-0 text-[10px] font-semibold text-brand-blue"
              >
                Trade price
              </Badge>
            ) : null}
          </div>
          <Link href={item.href as Route}>
            <h3 className="mt-0.5 line-clamp-2 text-sm font-semibold text-brand-navy transition-colors hover:text-brand-blue sm:text-base">
              {item.name}
            </h3>
          </Link>
          <p className="mt-1 font-mono text-[11px] text-muted-foreground">
            SKU: {item.sku}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <QuantitySelector
            value={item.quantity}
            onChange={(quantity) => onQuantityChange(item.id, quantity)}
            max={item.maxQuantity ?? 99}
          />
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-9 gap-1.5 text-muted-foreground hover:text-error"
            onClick={() => onRemove(item.id)}
          >
            <Trash2 className="size-4" />
            Remove
          </Button>
        </div>
      </div>

      <div className="flex items-center justify-between gap-4 sm:flex-col sm:items-end sm:justify-center sm:text-right">
        <div className="text-sm sm:hidden">
          {hasTradeDiscount ? (
            <>
              <p className="font-semibold tabular-nums text-brand-blue">
                {formatAud(item.tradePriceValue!)} each
              </p>
              <p className="text-xs text-muted-foreground line-through">
                {formatAud(item.priceValue)} retail
              </p>
            </>
          ) : (
            <p className="text-muted-foreground">
              {formatAud(item.priceValue)} each
            </p>
          )}
        </div>
        <div>
          {hasTradeDiscount ? (
            <>
              <p className="text-lg font-bold tabular-nums text-brand-blue">
                {formatAud(tradeLineTotal!)}
              </p>
              <p className="text-xs text-muted-foreground line-through">
                {formatAud(lineTotal)} retail
              </p>
              <p className="hidden text-xs text-muted-foreground sm:block">
                {formatAud(item.tradePriceValue!)} trade · GST incl.
              </p>
            </>
          ) : (
            <>
              <p className="text-lg font-bold tabular-nums text-brand-navy">
                {formatAud(lineTotal)}
              </p>
              <p className="hidden text-xs text-muted-foreground sm:block">
                {formatAud(item.priceValue)} each · GST incl.
              </p>
            </>
          )}
        </div>
      </div>
    </article>
  );
}

export { CartLineItem };
