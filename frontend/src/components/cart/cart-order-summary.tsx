"use client";

import Link from "next/link";
import { ArrowLeft, ArrowRight, Lock, Truck } from "lucide-react";

import type { CartSummary } from "@/types/cart";
import { formatAud } from "@/lib/cart";
import { cn } from "@/lib/utils";
import { CartTradeSummary } from "@/components/cart/cart-trade-summary";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export interface CartOrderSummaryProps {
  summary: CartSummary;
  className?: string;
}

function CartOrderSummary({ summary, className }: CartOrderSummaryProps) {
  return (
    <div className={cn("space-y-5", className)}>
      <aside className="rounded-xl border border-border bg-card p-5 shadow-sm md:p-6 lg:sticky lg:top-24">
        <h2 className="text-lg font-bold text-brand-navy">Order summary</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          {summary.itemCount} {summary.itemCount === 1 ? "item" : "items"} in cart
        </p>

        <dl className="mt-6 space-y-3 text-sm">
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Subtotal (inc. GST)</dt>
            <dd className="font-medium tabular-nums text-brand-navy">
              {formatAud(summary.subtotalIncGst)}
            </dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="flex items-center gap-1.5 text-muted-foreground">
              <Truck className="size-3.5" aria-hidden />
              Shipping estimate
            </dt>
            <dd className="font-medium tabular-nums text-brand-navy">
              {summary.shippingIncGst === 0 ? (
                <span className="text-success">Free</span>
              ) : (
                formatAud(summary.shippingIncGst)
              )}
            </dd>
          </div>
        </dl>

        {!summary.qualifiesForFreeShipping ? (
          <p className="mt-3 rounded-lg bg-brand-blue-light/50 px-3 py-2 text-xs text-brand-navy">
            Add {formatAud(summary.amountUntilFreeShipping)} more for{" "}
            <span className="font-semibold">free delivery</span> Australia-wide.
          </p>
        ) : (
          <p className="mt-3 flex items-center gap-1.5 text-xs font-medium text-success">
            <Truck className="size-3.5" aria-hidden />
            You qualify for free delivery
          </p>
        )}

        <Separator className="my-5" />

        <dl className="space-y-2 text-sm">
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Subtotal (ex. GST)</dt>
            <dd className="tabular-nums">{formatAud(summary.subtotalExGst)}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">GST (10%)</dt>
            <dd className="tabular-nums">{formatAud(summary.gstAmount)}</dd>
          </div>
          <div className="flex justify-between gap-4 pt-2 text-base font-bold text-brand-navy">
            <dt>Total (inc. GST)</dt>
            <dd className="tabular-nums">{formatAud(summary.totalIncGst)}</dd>
          </div>
        </dl>

        <Badge
          variant="outline"
          className="mt-4 w-full justify-center border-brand-blue/25 bg-brand-blue-light/30 py-1.5 text-[11px] font-semibold uppercase tracking-wide text-brand-blue"
        >
          All prices include 10% GST
        </Badge>

        <div className="mt-6 hidden space-y-3 lg:block">
          <Button asChild type="button" size="lg" className="w-full gap-2">
            <Link href="/checkout">
              <Lock className="size-4" />
              Proceed to checkout
              <ArrowRight className="size-4" />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="w-full gap-2">
            <Link href="/products">
              <ArrowLeft className="size-4" />
              Continue shopping
            </Link>
          </Button>
        </div>

        <p className="mt-4 hidden text-center text-[11px] text-muted-foreground lg:block">
          Tax invoice provided on every order · Secure Australian checkout
        </p>
      </aside>

      <CartTradeSummary summary={summary} />
    </div>
  );
}

export { CartOrderSummary };
