"use client";

import { useState } from "react";
import { Plus, Search } from "lucide-react";
import { toast } from "sonner";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import {
  useAdminWarehouses,
  useCreateWarehouse,
  useUpdateWarehouse,
} from "@/lib/api/admin/hooks";
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

function WarehousesPageView() {
  const [search, setSearch] = useState("");
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [capacity, setCapacity] = useState("");
  const { data, isLoading, isError } = useAdminWarehouses({ search: search || undefined });
  const createWarehouse = useCreateWarehouse();
  const updateWarehouse = useUpdateWarehouse();

  const handleCreate = async () => {
    if (!code.trim() || !name.trim()) return;
    await createWarehouse.mutateAsync({
      code: code.trim().toUpperCase(),
      name: name.trim(),
      capacity_units: capacity ? Number(capacity) : 0,
    });
    setCode("");
    setName("");
    setCapacity("");
    toast.success("Warehouse created");
  };

  return (
    <AdminListPage
      title="Warehouses"
      description="Distribution centres and fulfilment locations across Australia."
      isLoading={isLoading}
      isError={isError}
      actions={
        <div className="flex flex-wrap items-center gap-2">
          <Input
            placeholder="Code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="h-9 w-24"
          />
          <Input
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="h-9 w-40"
          />
          <Input
            placeholder="Capacity"
            type="number"
            value={capacity}
            onChange={(e) => setCapacity(e.target.value)}
            className="h-9 w-28"
          />
          <Button size="sm" onClick={handleCreate} disabled={createWarehouse.isPending}>
            <Plus className="mr-2 size-4" />
            Add warehouse
          </Button>
        </div>
      }
    >
      <div className="mb-4 flex max-w-sm items-center gap-2">
        <Search className="size-4 text-muted-foreground" />
        <Input
          placeholder="Search warehouses…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <AdminCard title="Warehouses" contentClassName="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Code</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Location</TableHead>
              <TableHead className="text-right">SKUs</TableHead>
              <TableHead className="text-right">Total units</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.map((wh) => (
              <TableRow key={wh.id}>
                <TableCell className="font-mono font-medium">{wh.code}</TableCell>
                <TableCell>{wh.name}</TableCell>
                <TableCell className="text-muted-foreground">{wh.location}</TableCell>
                <TableCell className="text-right tabular-nums">{wh.skuCount.toLocaleString()}</TableCell>
                <TableCell className="text-right tabular-nums">{wh.totalUnits.toLocaleString()}</TableCell>
                <TableCell className="text-right">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      updateWarehouse.mutate(
                        { id: wh.id, is_active: false },
                        { onSuccess: () => toast.success("Warehouse deactivated") }
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

export { WarehousesPageView };
