"use client";

import type { AdminSupplier } from "@/lib/api/admin/types";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const statusVariant = {
  active: "success",
  inactive: "secondary",
  onboarding: "warning",
} as const;

export interface SupplierPanelProps {
  suppliers: AdminSupplier[];
}

function SupplierPanel({ suppliers }: SupplierPanelProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Supplier</TableHead>
          <TableHead className="text-right">Products</TableHead>
          <TableHead>Contact</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {suppliers.map((supplier) => (
          <TableRow key={supplier.id}>
            <TableCell className="font-medium">{supplier.name}</TableCell>
            <TableCell className="text-right tabular-nums">{supplier.productsSupplied}</TableCell>
            <TableCell>{supplier.contactPerson}</TableCell>
            <TableCell>
              <Badge variant={statusVariant[supplier.status]} className="capitalize">
                {supplier.status}
              </Badge>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { SupplierPanel };
