"use client";

import { useState } from "react";
import { Plus, Search } from "lucide-react";
import { toast } from "sonner";

import { SupplierPanel } from "@/components/admin/dashboard/supplier-panel";
import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { useAdminSuppliers, useCreateSupplier } from "@/lib/api/admin/hooks";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

function SuppliersPageView() {
  const [search, setSearch] = useState("");
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const { data, isLoading, isError } = useAdminSuppliers({ search: search || undefined });
  const createSupplier = useCreateSupplier();

  const handleCreate = async () => {
    if (!code.trim() || !name.trim()) return;
    await createSupplier.mutateAsync({
      code: code.trim().toUpperCase(),
      name: name.trim(),
      email: email || undefined,
    });
    setCode("");
    setName("");
    setEmail("");
    toast.success("Supplier created");
  };

  return (
    <AdminListPage
      title="Suppliers"
      description="Manage vendor relationships and purchase order sources."
      isLoading={isLoading}
      isError={isError}
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <Input placeholder="Code" value={code} onChange={(e) => setCode(e.target.value)} className="h-9 w-24" />
          <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} className="h-9 w-40" />
          <Input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="h-9 w-48" />
          <Button size="sm" onClick={handleCreate} disabled={createSupplier.isPending}>
            <Plus className="mr-2 size-4" />
            Add supplier
          </Button>
        </div>
      }
    >
      <div className="mb-4 flex max-w-sm items-center gap-2">
        <Search className="size-4 text-muted-foreground" />
        <Input
          placeholder="Search suppliers…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <AdminCard title="Suppliers" contentClassName="p-0">
        <SupplierPanel suppliers={data ?? []} />
      </AdminCard>
    </AdminListPage>
  );
}

export { SuppliersPageView };
