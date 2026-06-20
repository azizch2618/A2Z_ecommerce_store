"use client";

import Link from "next/link";
import { ArrowLeft, Calendar, Lock, ShieldCheck } from "lucide-react";

import type { CartItem } from "@/types/cart";
import type { CheckoutOrderTotals } from "@/types/checkout";
import { formatAud } from "@/lib/cart";
import { cn } from "@/lib/utils";
import { RemoteImage } from "@/components/ui/remote-image";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export interface CheckoutOrderSummaryProps {
  items: CartItem[];
  totals: CheckoutOrderTotals;
  estimatedDelivery: string;
  isSubmitting?: boolean;
  className?: string;
}

function CheckoutOrderSummary({
  items,
  totals,
  estimatedDelivery,
  isSubmitting = false,
  className,
}: CheckoutOrderSummaryProps) {
  return (
    <aside
      className={cn(
        "rounded-xl border border-border bg-card p-5 shadow-sm md:p-6 lg:sticky lg:top-24",
        className
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-brand-navy">Order summary</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {totals.itemCount} {totals.itemCount === 1 ? "item" : "items"} · AUD
          </p>
        </div>
        <Badge
          variant="outline"
          className="shrink-0 gap-1 border-success/30 bg-success/5 text-success"
        >
          <ShieldCheck className="size-3" aria-hidden />
          Secure
        </Badge>
      </div>

      <ul className="mt-5 max-h-72 space-y-4 overflow-y-auto pr-1">
        {items.map((item) => {
          const unitPrice = item.tradePriceValue ?? item.priceValue;
          const lineTotal = unitPrice * item.quantity;

          return (
            <li key={item.id} className="flex gap-3">
              <div className="relative size-14 shrink-0 overflow-hidden rounded-lg border border-border bg-neutral-50">
                <RemoteImage
                  src={item.imageSrc}
                  alt={item.imageAlt}
                  fill
                  sizes="56px"
                  className="object-cover"
                />
              </div>
              <div className="min-w-0 flex-1">
                <p className="line-clamp-2 text-sm font-medium text-brand-navy">
                  {item.name}
                </p>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  Qty {item.quantity} × {formatAud(unitPrice)}
                </p>
                {item.tradePriceValue !== undefined &&
                item.tradePriceValue < item.priceValue ? (
                  <p className="text-[10px] text-brand-blue">Trade unit price</p>
                ) : null}
              </div>
              <p className="shrink-0 text-sm font-semibold tabular-nums text-brand-navy">
                {formatAud(lineTotal)}
              </p>
            </li>
          );
        })}
      </ul>

      <Separator className="my-5" />

      <dl className="space-y-2.5 text-sm">
        <div className="flex justify-between gap-4">
          <dt className="text-muted-foreground">Subtotal (inc. GST)</dt>
          <dd className="font-medium tabular-nums text-brand-navy">
            {formatAud(totals.tradeSubtotalIncGst)}
          </dd>
        </div>
        {totals.hasTradePricing ? (
          <div className="flex justify-between gap-4 text-success">
            <dt>Trade discount</dt>
            <dd className="font-semibold tabular-nums">
              −{formatAud(totals.tradeDiscountIncGst)}
            </dd>
          </div>
        ) : null}
        <div className="flex justify-between gap-4">
          <dt className="text-muted-foreground">Shipping</dt>
          <dd className="font-medium tabular-nums text-brand-navy">
            {totals.shippingIncGst === 0 ? (
              <span className="text-success">Free</span>
            ) : (
              formatAud(totals.shippingIncGst)
            )}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-muted-foreground">GST (10%)</dt>
          <dd className="tabular-nums">{formatAud(totals.gstAmount)}</dd>
        </div>
        <div className="flex justify-between gap-4 border-t border-border pt-3 text-base font-bold text-brand-navy">
          <dt>Grand total</dt>
          <dd className="tabular-nums">{formatAud(totals.totalIncGst)}</dd>
        </div>
      </dl>

      <div className="mt-4 flex flex-wrap gap-2">
        <Badge
          variant="outline"
          className="border-brand-blue/25 bg-brand-blue-light/30 text-[11px] font-semibold uppercase tracking-wide text-brand-blue"
        >
          GST included
        </Badge>
        <Badge
          variant="outline"
          className="gap-1 border-border text-[11px] font-medium text-muted-foreground"
        >
          <Lock className="size-3" aria-hidden />
          Secure checkout
        </Badge>
      </div>

      <div className="mt-4 flex items-center gap-2 rounded-lg border border-border/80 bg-muted/30 px-3 py-2.5">
        <Calendar className="size-4 shrink-0 text-brand-blue" aria-hidden />
        <p className="text-xs text-brand-navy">
          <span className="font-semibold">Estimated delivery:</span>{" "}
          {estimatedDelivery}
        </p>
      </div>

      <div className="mt-6 space-y-3">
        <Button
          type="submit"
          form="checkout-form"
          size="lg"
          className="hidden w-full gap-2 lg:flex"
          loading={isSubmitting}
        >
          <Lock className="size-4" />
          Place order · {formatAud(totals.totalIncGst)}
        </Button>
        <Button
          type="submit"
          form="checkout-form"
          size="lg"
          className="w-full gap-2 lg:hidden"
          loading={isSubmitting}
        >
          <Lock className="size-4" />
          Place order
        </Button>
        <Button asChild variant="outline" size="lg" className="w-full gap-2">
          <Link href="/cart">
            <ArrowLeft className="size-4" />
            Return to cart
          </Link>
        </Button>
      </div>

      <p className="mt-4 text-center text-[11px] text-muted-foreground">
        Tax invoice emailed on dispatch · Mock checkout only
      </p>
    </aside>
  );
}

export { CheckoutOrderSummary };
