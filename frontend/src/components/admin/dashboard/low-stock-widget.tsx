"use client";

import type { LowStockItem } from "@/lib/api/admin/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export interface LowStockWidgetProps {
  items: LowStockItem[];
}

function LowStockWidget({ items }: LowStockWidgetProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Product</TableHead>
          <TableHead>SKU</TableHead>
          <TableHead>Warehouse</TableHead>
          <TableHead className="text-right">Stock</TableHead>
          <TableHead className="text-right">Reorder</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.map((item) => (
          <TableRow key={item.id}>
            <TableCell className="font-medium">{item.productName}</TableCell>
            <TableCell className="font-mono text-xs text-muted-foreground">{item.sku}</TableCell>
            <TableCell>{item.warehouse}</TableCell>
            <TableCell className="text-right">
              <Badge variant="warning">{item.currentStock}</Badge>
            </TableCell>
            <TableCell className="text-right text-muted-foreground">{item.reorderLevel}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { LowStockWidget };
