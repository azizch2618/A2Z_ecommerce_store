"use client";

import { Plus } from "lucide-react";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { useAdminProducts } from "@/lib/api/admin/hooks";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function formatAud(cents: number) {
  return new Intl.NumberFormat("en-AU", { style: "currency", currency: "AUD" }).format(
    cents / 100
  );
}

function ProductsPageView() {
  const { data, isLoading, isError } = useAdminProducts();

  return (
    <AdminListPage
      title="Products"
      description="Manage catalog products, pricing, and stock visibility."
      isLoading={isLoading}
      isError={isError}
      actions={
        <Button size="sm">
          <Plus className="mr-2 size-4" />
          Add product
        </Button>
      }
    >
      <AdminCard title="Product catalog" description={`${data?.length ?? 0} products`} contentClassName="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>SKU</TableHead>
              <TableHead>Brand</TableHead>
              <TableHead>Category</TableHead>
              <TableHead className="text-right">Price (inc GST)</TableHead>
              <TableHead className="text-right">Stock</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.map((product) => (
              <TableRow key={product.id}>
                <TableCell className="font-medium">{product.name}</TableCell>
                <TableCell className="font-mono text-xs">{product.sku}</TableCell>
                <TableCell>{product.brand}</TableCell>
                <TableCell>{product.category}</TableCell>
                <TableCell className="text-right tabular-nums">
                  {formatAud(Math.round(product.priceCents * 1.1))}
                </TableCell>
                <TableCell className="text-right">
                  <Badge variant={product.stock === 0 ? "destructive" : product.stock < 10 ? "warning" : "secondary"}>
                    {product.stock}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge variant={product.status === "active" ? "success" : "secondary"} className="capitalize">
                    {product.status}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </AdminCard>
    </AdminListPage>
  );
}

export { ProductsPageView };
