"use client";

import { useState } from "react";
import { Plus, Search } from "lucide-react";
import { toast } from "sonner";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { useAdminBrands, useCreateBrand, useUpdateBrand } from "@/lib/api/admin/hooks";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function BrandsPageView() {
  const [search, setSearch] = useState("");
  const [newName, setNewName] = useState("");
  const [logoUrl, setLogoUrl] = useState("");
  const { data, isLoading, isError } = useAdminBrands({ search: search || undefined });
  const createBrand = useCreateBrand();
  const updateBrand = useUpdateBrand();

  const handleCreate = async () => {
    if (!newName.trim()) return;
    await createBrand.mutateAsync({
      name: newName.trim(),
      logo_url: logoUrl || undefined,
      featured: true,
    });
    setNewName("");
    setLogoUrl("");
    toast.success("Brand created");
  };

  return (
    <AdminListPage
      title="Brands"
      description="Manage manufacturer brands and featured placements."
      isLoading={isLoading}
      isError={isError}
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <Input
            placeholder="Brand name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="h-9 w-40"
          />
          <Input
            placeholder="Logo URL"
            value={logoUrl}
            onChange={(e) => setLogoUrl(e.target.value)}
            className="h-9 w-48"
          />
          <Button size="sm" onClick={handleCreate} disabled={createBrand.isPending}>
            <Plus className="mr-2 size-4" />
            Add brand
          </Button>
        </div>
      }
    >
      <div className="mb-4 flex max-w-sm items-center gap-2">
        <Search className="size-4 text-muted-foreground" />
        <Input
          placeholder="Search brands…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <AdminCard title="Brands" contentClassName="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Slug</TableHead>
              <TableHead className="text-right">Products</TableHead>
              <TableHead>Featured</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.map((brand) => (
              <TableRow key={brand.id}>
                <TableCell className="font-medium">{brand.name}</TableCell>
                <TableCell className="font-mono text-xs text-muted-foreground">{brand.slug}</TableCell>
                <TableCell className="text-right tabular-nums">{brand.productCount}</TableCell>
                <TableCell>
                  <Badge variant={brand.featured ? "trade" : "secondary"}>
                    {brand.featured ? "Featured" : "Standard"}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      updateBrand.mutate(
                        { id: brand.id, featured: !brand.featured },
                        { onSuccess: () => toast.success("Brand updated") }
                      )
                    }
                  >
                    Toggle featured
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </AdminCard>
    </AdminListPage>
  );
}

export { BrandsPageView };
