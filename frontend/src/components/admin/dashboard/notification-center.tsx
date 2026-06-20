"use client";

import { Bell, CreditCard, Handshake, Package } from "lucide-react";

import type { AdminNotification } from "@/lib/api/admin/types";
import { useAdminDashboard } from "@/lib/api/admin/hooks";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/utils";

const typeIcons = {
  low_stock: Package,
  new_order: Bell,
  trade_application: Handshake,
  payment: CreditCard,
} as const;

function formatRelativeTime(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const hours = Math.floor(diff / 3_600_000);
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export interface NotificationCenterProps {
  notifications?: AdminNotification[];
}

function NotificationCenter({ notifications: notificationsProp }: NotificationCenterProps) {
  const { data, isLoading, isError, error } = useAdminDashboard();

  if (notificationsProp !== undefined) {
    return (
      <NotificationDropdown
        notifications={notificationsProp}
        isLoading={false}
        isError={false}
      />
    );
  }

  return (
    <NotificationDropdown
      notifications={data?.notifications ?? []}
      isLoading={isLoading}
      isError={isError}
      errorMessage={error instanceof Error ? error.message : undefined}
    />
  );
}

function NotificationDropdown({
  notifications,
  isLoading,
  isError,
  errorMessage,
}: {
  notifications: AdminNotification[];
  isLoading: boolean;
  isError: boolean;
  errorMessage?: string;
}) {
  const unread = notifications.filter((n) => !n.read).length;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" className="relative size-9" aria-label="Notifications">
          <Bell className="size-4" />
          {!isError && unread > 0 ? (
            <span className="absolute -right-1 -top-1 flex size-4 items-center justify-center rounded-full bg-brand-amber text-[10px] font-bold text-brand-navy">
              {unread}
            </span>
          ) : null}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel>Notifications</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {isLoading ? (
          <div className="flex items-center justify-center py-6">
            <Spinner className="size-5" />
          </div>
        ) : isError ? (
          <p className="px-2 py-4 text-center text-sm text-destructive">
            {errorMessage ?? "Failed to load notifications."}
          </p>
        ) : notifications.length === 0 ? (
          <p className="px-2 py-4 text-center text-sm text-muted-foreground">No notifications</p>
        ) : (
          notifications.slice(0, 6).map((n) => {
            const Icon = typeIcons[n.type];
            return (
              <div
                key={n.id}
                className={cn(
                  "flex gap-3 px-2 py-2.5",
                  !n.read && "bg-brand-amber/5"
                )}
              >
                <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted">
                  <Icon className="size-4 text-muted-foreground" />
                </span>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-foreground">{n.title}</p>
                  <p className="text-xs text-muted-foreground line-clamp-2">{n.message}</p>
                  <p className="mt-0.5 text-[10px] text-muted-foreground">
                    {formatRelativeTime(n.createdAt)}
                  </p>
                </div>
              </div>
            );
          })
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export { NotificationCenter };
