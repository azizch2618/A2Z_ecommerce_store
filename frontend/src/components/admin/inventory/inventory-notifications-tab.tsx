"use client";

import { Bell } from "lucide-react";

import { AdminCard } from "@/components/admin/shared/admin-card";
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
import {
  useAcknowledgeNotification,
  useInventoryNotifications,
  useNotificationUnreadCount,
} from "@/lib/api/admin/inventory-hooks";
import { hasAuthTokens } from "@/lib/api/auth/token-storage";

function NotificationsTab() {
  const { data: notifications, isLoading } = useInventoryNotifications("active");
  const { data: countData } = useNotificationUnreadCount();
  const acknowledge = useAcknowledgeNotification();

  if (!hasAuthTokens()) {
    return (
      <AdminCard title="Low stock notifications">
        <p className="text-sm text-muted-foreground">
          Notifications are generated when stock crosses reorder levels. Sign in
          to receive live alerts from the inventory API.
        </p>
      </AdminCard>
    );
  }

  return (
    <AdminCard
      title="Low stock notifications"
      description="Alerts are created automatically when on-hand quantity falls to the reorder point or below."
      action={
        countData && countData.count > 0 ? (
          <Badge variant="warning" className="gap-1">
            <Bell className="size-3" />
            {countData.count} unread
          </Badge>
        ) : null
      }
      contentClassName="p-0"
    >
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>SKU</TableHead>
            <TableHead>Warehouse</TableHead>
            <TableHead>Alert</TableHead>
            <TableHead>Message</TableHead>
            <TableHead className="text-right">On hand</TableHead>
            <TableHead />
          </TableRow>
        </TableHeader>
        <TableBody>
          {isLoading ? (
            <TableRow>
              <TableCell colSpan={6} className="text-muted-foreground">
                Loading notifications…
              </TableCell>
            </TableRow>
          ) : null}
          {notifications?.data.map((n) => (
            <TableRow key={n.id}>
              <TableCell className="font-mono text-xs">{n.sku}</TableCell>
              <TableCell>{n.warehouse_code}</TableCell>
              <TableCell>
                <Badge variant={n.alert_type === "out_of_stock" ? "destructive" : "warning"}>
                  {n.alert_type === "out_of_stock" ? "Out of stock" : "Low stock"}
                </Badge>
              </TableCell>
              <TableCell className="max-w-xs truncate text-sm">{n.message}</TableCell>
              <TableCell className="text-right">{n.quantity_on_hand}</TableCell>
              <TableCell className="text-right">
                <Button
                  size="sm"
                  variant="outline"
                  disabled={acknowledge.isPending}
                  onClick={() => acknowledge.mutate(n.id)}
                >
                  Acknowledge
                </Button>
              </TableCell>
            </TableRow>
          ))}
          {!isLoading && notifications?.data.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-muted-foreground">
                No active low-stock notifications.
              </TableCell>
            </TableRow>
          ) : null}
        </TableBody>
      </Table>
    </AdminCard>
  );
}

export { NotificationsTab };
