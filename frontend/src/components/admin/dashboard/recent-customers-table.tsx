"use client";

import type { AdminCustomer } from "@/lib/api/admin/types";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function formatDate(date: string) {
  return new Intl.DateTimeFormat("en-AU", { dateStyle: "medium" }).format(new Date(date));
}

export interface RecentCustomersTableProps {
  customers: AdminCustomer[];
}

function RecentCustomersTable({ customers }: RecentCustomersTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Email</TableHead>
          <TableHead className="text-right">Orders</TableHead>
          <TableHead>Trade status</TableHead>
          <TableHead>Joined</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {customers.map((customer) => (
          <TableRow key={customer.id}>
            <TableCell className="font-medium">{customer.name}</TableCell>
            <TableCell className="text-muted-foreground">{customer.email}</TableCell>
            <TableCell className="text-right tabular-nums">{customer.orderCount}</TableCell>
            <TableCell>
              {customer.tradeStatus ? (
                <Badge
                  variant={
                    customer.tradeStatus === "approved"
                      ? "success"
                      : customer.tradeStatus === "pending"
                        ? "warning"
                        : "destructive"
                  }
                  className="capitalize"
                >
                  {customer.tradeStatus}
                </Badge>
              ) : (
                <span className="text-sm text-muted-foreground">Retail</span>
              )}
            </TableCell>
            <TableCell className="text-sm text-muted-foreground">
              {formatDate(customer.joinedAt)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { RecentCustomersTable };
