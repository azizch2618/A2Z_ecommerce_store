"use client";

import type { ReactNode } from "react";
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function CompareTable() {
  const { products } = useCompare();

  const compareSpecRows = React.useMemo(() => {
    const labels = new Set<string>();
    for (const product of products) {
      Object.keys(product.specs).forEach((key) => labels.add(key));
    }
    return Array.from(labels).map((key) => ({ key, label: key }));
  }, [products]);

  const detailRows: Array<{
    label: string;
    render: (product: CompareProduct) => ReactNode;
  }> = [
    {
      label: "Product name",
      render: (product) => (
        <Link
          href={product.href as Route}
          className="font-semibold text-foreground hover:text-brand-blue"
        >
          {product.name}
        </Link>
      ),
    },
    {
      label: "Brand",
      render: (product) => (
        <span className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
          {product.brand}
        </span>
      ),
    },
    {
      label: "SKU",
      render: (product) => (
        <span className="font-mono text-xs text-muted-foreground">{product.sku}</span>
      ),
    },
    {
      label: "Price",
      render: (product) => (
        <span className="font-semibold tabular-nums">{formatAud(product.priceIncGst)}</span>
      ),
    },
    {
      label: "Trade price",
      render: (product) =>
        product.tradePriceIncGst !== undefined ? (
          <span className="font-semibold tabular-nums text-brand-blue">
            {formatAud(product.tradePriceIncGst)}
          </span>
        ) : (
          <span className="text-muted-foreground">—</span>
        ),
    },
    {
      label: "Rating",
      render: (product) =>
        product.rating !== undefined ? (
          <ProductRating
            rating={product.rating}
            reviewCount={product.reviewCount}
            size="sm"
          />
        ) : (
          <span className="text-muted-foreground">—</span>
        ),
    },
    {
      label: "Stock status",
      render: (product) => <ProductStockBadge status={product.stock} size="sm" />,
    },
  ];

  return (
    <div className="hidden overflow-hidden rounded-xl border border-border bg-card shadow-sm lg:block">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead className="sticky left-0 z-10 min-w-[160px] bg-card font-semibold text-foreground">
              Compare
            </TableHead>
            {products.map((product) => (
              <TableHead
                key={product.id}
                className="min-w-[220px] align-top"
              >
                <Link
                  href={product.href as Route}
                  className="relative mx-auto block aspect-[4/3] w-full max-w-[200px] overflow-hidden rounded-lg border border-border bg-muted"
                >
                  <RemoteImage
                    src={product.imageSrc}
                    alt={product.imageAlt}
                    fill
                    sizes="200px"
                    className="object-cover"
                  />
                </Link>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {detailRows.map((row) => (
            <TableRow key={row.label}>
              <TableCell className="sticky left-0 z-10 bg-card font-medium text-muted-foreground">
                {row.label}
              </TableCell>
              {products.map((product) => (
                <TableCell key={`${product.id}-${row.label}`}>{row.render(product)}</TableCell>
              ))}
            </TableRow>
          ))}

          <TableRow className="bg-muted/30 hover:bg-muted/30">
            <TableCell
              colSpan={products.length + 1}
              className="sticky left-0 py-3 text-xs font-bold uppercase tracking-wider text-foreground"
            >
              Specifications
            </TableCell>
          </TableRow>

          {compareSpecRows.map((row) => (
            <TableRow key={row.key}>
              <TableCell className="sticky left-0 z-10 bg-card font-medium text-muted-foreground">
                {row.label}
              </TableCell>
              {products.map((product) => (
                <TableCell key={`${product.id}-${row.key}`} className="text-sm">
                  {product.specs[row.key] ?? "—"}
                </TableCell>
              ))}
            </TableRow>
          ))}

          <TableRow>
            <TableCell className="sticky left-0 z-10 bg-card font-medium text-muted-foreground">
              Actions
            </TableCell>
            {products.map((product) => (
              <TableCell key={`${product.id}-actions`} className="align-top">
                <CompareProductActions product={product} />
              </TableCell>
            ))}
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}

export { CompareTable };
