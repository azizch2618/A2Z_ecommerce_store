"use client";

import { useState } from "react";
import { Plus, Search } from "lucide-react";
import { toast } from "sonner";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { useAdminCategories, useCreateCategory, useUpdateCategory } from "@/lib/api/admin/hooks";
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

function CategoriesPageView() {
  const [search, setSearch] = useState("");
  const [newName, setNewName] = useState("");
  const { data, isLoading, isError } = useAdminCategories({ search: search || undefined });
  const createCategory = useCreateCategory();
  const updateCategory = useUpdateCategory();

  const handleCreate = async () => {
    if (!newName.trim()) return;
    await createCategory.mutateAsync({ name: newName.trim() });
    setNewName("");
    toast.success("Category created");
  };

  return (
    <AdminListPage
      title="Categories"
      description="Organise products into hierarchical categories."
      isLoading={isLoading}
      isError={isError}
      actions={
        <div className="flex items-center gap-2">
          <Input
            placeholder="New category name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="h-9 w-48"
          />
          <Button size="sm" onClick={handleCreate} disabled={createCategory.isPending}>
            <Plus className="mr-2 size-4" />
            Add category
          </Button>
        </div>
      }
    >
      <div className="mb-4 flex max-w-sm items-center gap-2">
        <Search className="size-4 text-muted-foreground" />
        <Input
          placeholder="Search categories…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <AdminCard title="Category tree" contentClassName="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Slug</TableHead>
              <TableHead>Parent</TableHead>
              <TableHead className="text-right">Products</TableHead>
              <TableHead className="text-right">Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.map((cat) => (
              <TableRow key={cat.id}>
                <TableCell className="font-medium">{cat.name}</TableCell>
                <TableCell className="font-mono text-xs text-muted-foreground">{cat.slug}</TableCell>
                <TableCell>{cat.parent ?? "—"}</TableCell>
                <TableCell className="text-right tabular-nums">{cat.productCount}</TableCell>
                <TableCell className="text-right">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      updateCategory.mutate(
                        { id: cat.id, is_active: false },
                        { onSuccess: () => toast.success("Category deactivated") }
                      )
                    }
                  >
                    Deactivate
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

export { CategoriesPageView };
