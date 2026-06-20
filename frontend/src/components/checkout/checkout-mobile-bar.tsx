"use client";

import Link from "next/link";
import { Lock } from "lucide-react";

import type { CheckoutOrderTotals } from "@/types/checkout";
import { formatAud } from "@/lib/cart";
import { Button } from "@/components/ui/button";

export interface CheckoutMobileBarProps {
  totals: CheckoutOrderTotals;
  isSubmitting?: boolean;
}

function CheckoutMobileBar({ totals, isSubmitting = false }: CheckoutMobileBarProps) {
  return (
    <div className="fixed inset-x-0 bottom-14 z-sticky border-t border-border bg-background/95 shadow-lg backdrop-blur-md lg:hidden">
      <div className="container-app flex items-center gap-3 p-3">
        <div className="min-w-0 flex-1">
          <p className="text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
            Grand total
          </p>
          <p className="text-lg font-bold tabular-nums text-brand-navy">
            {formatAud(totals.totalIncGst)}
          </p>
          <p className="text-[10px] text-muted-foreground">GST included</p>
        </div>
        <Button
          type="submit"
          form="checkout-form"
          className="shrink-0 gap-2"
          loading={isSubmitting}
        >
          <Lock className="size-4" />
          Place order
        </Button>
        <Button asChild variant="outline" size="sm" className="shrink-0">
          <Link href="/cart">Cart</Link>
        </Button>
      </div>
    </div>
  );
}

export { CheckoutMobileBar };
