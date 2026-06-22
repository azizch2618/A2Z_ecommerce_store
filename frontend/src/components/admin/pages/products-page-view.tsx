"use client";

import { useState } from "react";
import { Download, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { ProductFormSheet } from "@/components/admin/pages/product-form-sheet";
import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import {
  useAdminProducts,
  useCreateProduct,
  useDeleteProduct,
  useUpdateProduct,
} from "@/lib/api/admin/hooks";
import type { AdminProduct } from "@/lib/api/admin/types";
import { downloadTextFile } from "@/lib/admin/download-text-file";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
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

function exportProductsCatalog(products: AdminProduct[]) {
  const rows = [
    ["name", "sku", "brand", "category", "price_ex_gst_cents", "cost_cents", "stock", "status"],
    ...products.map((product) => [
      product.name,
      product.sku,
      product.brand,
      product.category,
      String(product.sellPriceExGstCents),
      String(product.costPriceCents),
      String(product.stock),
      product.status,
    ]),
  ];
  const csv = rows.map((row) => row.map((cell) => `"${cell.replace(/"/g, '""')}"`).join(",")).join("\n");
  downloadTextFile("products-catalog.csv", csv, "text/csv;charset=utf-8");
}

function ProductsPageView() {
  const [search, setSearch] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<AdminProduct | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<AdminProduct | null>(null);

  const { data, isLoading, isError } = useAdminProducts({ search: search || undefined });
  const createProduct = useCreateProduct();
  const updateProduct = useUpdateProduct();
  const deleteProduct = useDeleteProduct();

  const openCreate = () => {
    setEditingProduct(null);
    setFormOpen(true);
  };

  const openEdit = (product: AdminProduct) => {
    setEditingProduct(product);
    setFormOpen(true);
  };

  const handleExportCatalog = () => {
    if (!data?.length) {
      toast.error("No products to export");
      return;
    }
    exportProductsCatalog(data);
    toast.success("Product catalog exported");
  };

  const handleFormSubmit = async (payload: Parameters<typeof createProduct.mutateAsync>[0]) => {
    try {
      if (editingProduct) {
        await updateProduct.mutateAsync({ id: editingProduct.id, ...payload });
        toast.success("Product updated");
      } else {
        await createProduct.mutateAsync(payload);
        toast.success("Product created");
      }
      setFormOpen(false);
      setEditingProduct(null);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to save product");
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteProduct.mutateAsync(deleteTarget.id);
      toast.success("Product deleted");
      setDeleteTarget(null);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to delete product");
    }
  };

  return (
    <>
      <AdminListPage
        title="Products"
        description="Manage catalog products, pricing, stock, and images."
        isLoading={isLoading}
        isError={isError}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <Button size="sm" variant="outline" onClick={handleExportCatalog}>
              <Download className="mr-2 size-4" />
              Export catalog
            </Button>
            <Button size="sm" onClick={openCreate}>
              <Plus className="mr-2 size-4" />
              Add product
            </Button>
          </div>
        }
      >
        <div className="mb-4 flex max-w-sm items-center gap-2">
          <Search className="size-4 text-muted-foreground" />
          <Input
            placeholder="Search products…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <AdminCard title="Product catalog" description={`${data?.length ?? 0} products`} contentClassName="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>SKU</TableHead>
                <TableHead>Brand</TableHead>
                <TableHead>Category</TableHead>
                <TableHead className="text-right">Sell (ex GST)</TableHead>
                <TableHead className="text-right">Cost</TableHead>
                <TableHead className="text-right">Stock</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.map((product) => (
                <TableRow key={product.id}>
                  <TableCell className="font-medium">{product.name}</TableCell>
                  <TableCell className="font-mono text-xs">{product.sku}</TableCell>
                  <TableCell>{product.brand || "—"}</TableCell>
                  <TableCell>{product.category || "—"}</TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatAud(product.sellPriceExGstCents)}
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {formatAud(product.costPriceCents)}
                  </TableCell>
                  <TableCell className="text-right">
                    <Badge
                      variant={
                        product.stock === 0 ? "destructive" : product.stock < 10 ? "warning" : "secondary"
                      }
                    >
                      {product.stock}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={product.status === "active" ? "success" : "secondary"}
                      className="capitalize"
                    >
                      {product.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Button size="sm" variant="outline" onClick={() => openEdit(product)}>
                        <Pencil className="size-4" />
                        <span className="sr-only">Edit</span>
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => setDeleteTarget(product)}>
                        <Trash2 className="size-4" />
                        <span className="sr-only">Delete</span>
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </AdminCard>
      </AdminListPage>

      <ProductFormSheet
        open={formOpen}
        onOpenChange={(open) => {
          setFormOpen(open);
          if (!open) setEditingProduct(null);
        }}
        product={editingProduct}
        onSubmit={handleFormSubmit}
        isSubmitting={createProduct.isPending || updateProduct.isPending}
      />

      <Dialog open={Boolean(deleteTarget)} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete product</DialogTitle>
            <DialogDescription>
              {deleteTarget
                ? `Remove "${deleteTarget.name}" from the catalog? This soft-deletes the product and marks it inactive.`
                : null}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => void handleDelete()}
              disabled={deleteProduct.isPending}
            >
              Delete product
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}

export { ProductsPageView };
