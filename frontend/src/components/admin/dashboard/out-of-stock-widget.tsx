"use client";

import type { OutOfStockItem } from "@/lib/api/admin/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export interface OutOfStockWidgetProps {
  items: OutOfStockItem[];
}

function OutOfStockWidget({ items }: OutOfStockWidgetProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Product</TableHead>
          <TableHead>SKU</TableHead>
          <TableHead>Warehouse</TableHead>
          <TableHead>Last sold</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.map((item) => (
          <TableRow key={item.id}>
            <TableCell className="font-medium">{item.productName}</TableCell>
            <TableCell className="font-mono text-xs text-muted-foreground">{item.sku}</TableCell>
            <TableCell>{item.warehouse}</TableCell>
            <TableCell>
              <Badge variant="destructive">Out of stock</Badge>
              <span className="ml-2 text-xs text-muted-foreground">{item.lastSoldAt}</span>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { OutOfStockWidget };
