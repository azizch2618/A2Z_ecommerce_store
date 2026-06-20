"use client";

import Link from "next/link";
import { BadgePercent, Sparkles } from "lucide-react";

import type { CartSummary } from "@/types/cart";
import { formatAud } from "@/lib/cart";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

export interface CartTradeSummaryProps {
  summary: CartSummary;
  className?: string;
}

function CartTradeSummary({ summary, className }: CartTradeSummaryProps) {
  if (!summary.hasTradePricing) {
    return null;
  }

  return (
    <section
      aria-label="Trade pricing summary"
      className={cn(
        "rounded-xl border border-brand-blue/20 bg-gradient-to-br from-brand-blue-light/40 via-card to-card p-5 shadow-sm",
        className
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="size-4 text-brand-blue" aria-hidden />
            <h3 className="text-sm font-bold text-brand-navy">Trade pricing summary</h3>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">
            Verified trade account rates applied to eligible lines.
          </p>
        </div>
        <Badge className="shrink-0 bg-brand-blue text-white hover:bg-brand-blue">
          Trade
        </Badge>
      </div>

      <dl className="mt-5 space-y-2.5 text-sm">
        <div className="flex justify-between gap-4">
          <dt className="text-muted-foreground">Trade subtotal (inc. GST)</dt>
          <dd className="font-semibold tabular-nums text-brand-navy">
            {formatAud(summary.tradeSubtotalIncGst)}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-muted-foreground">Shipping (trade estimate)</dt>
          <dd className="font-medium tabular-nums text-brand-navy">
            {summary.tradeShippingIncGst === 0 ? (
              <span className="text-success">Free</span>
            ) : (
              formatAud(summary.tradeShippingIncGst)
            )}
          </dd>
        </div>
        <div className="flex justify-between gap-4">
          <dt className="text-muted-foreground">GST on trade total (10%)</dt>
          <dd className="tabular-nums">{formatAud(summary.tradeGstAmount)}</dd>
        </div>
      </dl>

      <div className="mt-4 flex items-center gap-2 rounded-lg border border-success/25 bg-success/5 px-3 py-2.5">
        <BadgePercent className="size-4 shrink-0 text-success" aria-hidden />
        <p className="text-xs text-brand-navy">
          You save{" "}
          <span className="font-bold text-success">
            {formatAud(summary.tradeSavingsIncGst)}
          </span>{" "}
          vs retail on this order.
        </p>
      </div>

      <Separator className="my-4" />

      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs text-muted-foreground">Trade total (inc. GST)</p>
          <p className="text-xs text-muted-foreground">
            Ex GST {formatAud(summary.tradeSubtotalExGst)}
          </p>
        </div>
        <p className="text-2xl font-bold tabular-nums text-brand-blue">
          {formatAud(summary.tradeTotalIncGst)}
        </p>
      </div>

      <Button
        asChild
        variant="link"
        size="sm"
        className="mt-3 h-auto p-0 text-xs text-brand-blue"
      >
        <Link href="/trade">Learn about trade accounts</Link>
      </Button>
    </section>
  );
}

export { CartTradeSummary };
