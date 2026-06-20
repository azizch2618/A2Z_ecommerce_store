"use client";

import Link from "next/link";
import type { Route } from "next";
import * as React from "react";

import type { CompareProduct } from "@/types/compare";
import { formatAud } from "@/lib/cart";
import { CompareProductActions } from "@/components/compare/compare-product-actions";
import { useCompare } from "@/components/compare/compare-provider";
import { ProductRating } from "@/components/product/product-rating";
import { ProductStockBadge } from "@/components/product/product-stock-badge";
import { RemoteImage } from "@/components/ui/remote-image";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

function SpecRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5 py-2 sm:flex-row sm:justify-between sm:gap-4">
      <dt className="text-xs font-medium text-muted-foreground">{label}</dt>
      <dd className="text-sm text-foreground sm:text-right">{value}</dd>
    </div>
  );
}

function CompareMobileCard({
  product,
  specRows,
}: {
  product: CompareProduct;
  specRows: Array<{ key: string; label: string }>;
}) {
  const hasTradePrice =
    product.tradePriceIncGst !== undefined &&
    product.tradePriceIncGst < product.priceIncGst;

  return (
    <Card className="overflow-hidden">
      <CardHeader className="space-y-4 p-4 pb-0">
        <Link
          href={product.href as Route}
          className="relative block aspect-[16/10] overflow-hidden rounded-lg border border-border bg-muted"
        >
          <RemoteImage
            src={product.imageSrc}
            alt={product.imageAlt}
            fill
            sizes="100vw"
            className="object-cover"
          />
        </Link>
        <div>
          <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
            {product.brand}
          </p>
          <Link href={product.href as Route}>
            <h3 className="mt-1 text-base font-semibold text-foreground hover:text-brand-blue">
              {product.name}
            </h3>
          </Link>
          <p className="mt-1 font-mono text-[11px] text-muted-foreground">
            SKU: {product.sku}
          </p>
        </div>
      </CardHeader>

      <CardContent className="space-y-4 p-4">
        <div className="flex flex-wrap items-center gap-2">
          <ProductStockBadge status={product.stock} size="sm" />
          {hasTradePrice ? (
            <Badge className="bg-brand-blue text-white hover:bg-brand-blue">Trade</Badge>
          ) : null}
        </div>

        <div className="flex flex-wrap items-baseline gap-2">
          <p className="text-xl font-bold tabular-nums text-foreground">
            {formatAud(hasTradePrice ? product.tradePriceIncGst! : product.priceIncGst)}
          </p>
          {hasTradePrice ? (
            <p className="text-sm text-muted-foreground line-through">
              {formatAud(product.priceIncGst)}
            </p>
          ) : null}
        </div>

        {product.rating !== undefined ? (
          <ProductRating
            rating={product.rating}
            reviewCount={product.reviewCount}
            size="sm"
          />
        ) : null}

        <Separator />

        <dl>
          <p className="mb-2 text-xs font-bold uppercase tracking-wider text-foreground">
            Specifications
          </p>
          {specRows.map((row) => (
            <SpecRow
              key={row.key}
              label={row.label}
              value={product.specs[row.key] ?? "—"}
            />
          ))}
        </dl>
      </CardContent>

      <CardFooter className="border-t border-border p-4">
        <CompareProductActions product={product} className="w-full" />
      </CardFooter>
    </Card>
  );
}

function CompareMobileCards() {
  const { products } = useCompare();

  const specRows = React.useMemo(() => {
    const labels = new Set<string>();
    for (const product of products) {
      Object.keys(product.specs).forEach((key) => labels.add(key));
    }
    return Array.from(labels).map((key) => ({ key, label: key }));
  }, [products]);

  return (
    <div className="space-y-5 lg:hidden">
      {products.map((product) => (
        <CompareMobileCard key={product.id} product={product} specRows={specRows} />
      ))}
    </div>
  );
}

export { CompareMobileCards };
