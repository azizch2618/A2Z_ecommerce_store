"use client";

import Link from "next/link";
import { ArrowRight, Lock } from "lucide-react";

import type { CartSummary } from "@/types/cart";
import { formatAud } from "@/lib/cart";
import { Button } from "@/components/ui/button";

export interface CartMobileBarProps {
  summary: CartSummary;
}

function CartMobileBar({ summary }: CartMobileBarProps) {
  const displayTotal = summary.hasTradePricing
    ? summary.tradeTotalIncGst
    : summary.totalIncGst;

  return (
    <div className="fixed inset-x-0 bottom-14 z-sticky border-t border-border bg-background/95 shadow-lg backdrop-blur-md lg:hidden">
      <div className="container-app flex items-center gap-3 p-3">
        <div className="min-w-0 flex-1">
          <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
            {summary.hasTradePricing ? "Trade total" : "Order total"}
          </p>
          <p className="text-lg font-bold tabular-nums text-brand-navy">
            {formatAud(displayTotal)}
          </p>
          {summary.hasTradePricing ? (
            <p className="text-[10px] text-success">
              Save {formatAud(summary.tradeSavingsIncGst)} with trade pricing
            </p>
          ) : (
            <p className="text-[10px] text-muted-foreground">GST included</p>
          )}
        </div>

        <Button asChild type="button" className="shrink-0 gap-2">
          <Link href="/checkout">
            <Lock className="size-4" />
            Checkout
            <ArrowRight className="size-4" />
          </Link>
        </Button>
      </div>
    </div>
  );
}

export { CartMobileBar };
