"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Building2,
  FolderTree,
  Handshake,
  LayoutDashboard,
  LineChart,
  Package,
  Contact2,
  FileText,
  Settings,
  ShoppingCart,
  Tag,
  Truck,
  Users,
  Warehouse,
} from "lucide-react";

import { adminNavItems } from "@/config/admin/nav";
import { usePermissions, useRoles } from "@/hooks/use-permissions";
import { hasPermission } from "@/lib/rbac";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

const iconMap = {
  "layout-dashboard": LayoutDashboard,
  package: Package,
  "folder-tree": FolderTree,
  tag: Tag,
  warehouse: Warehouse,
  "building-2": Building2,
  "shopping-cart": ShoppingCart,
  users: Users,
  handshake: Handshake,
  truck: Truck,
  "bar-chart-3": BarChart3,
  "line-chart": LineChart,
  "contact-2": Contact2,
  "file-text": FileText,
  settings: Settings,
} as const;

export interface AdminSidebarProps {
  className?: string;
  onNavigate?: () => void;
}

function AdminSidebar({ className, onNavigate }: AdminSidebarProps) {
  const pathname = usePathname();
  const { permissions } = usePermissions();
  const { user, roleLabel } = useRoles();
  const visibleNavItems = adminNavItems.filter((item) =>
    hasPermission(permissions, item.permission)
  );
  let lastSection: string | undefined;

  const displayName = user
    ? `${user.first_name} ${user.last_name}`.trim() || user.email
    : "Demo Admin";
  const initials = user
    ? `${user.first_name?.[0] ?? ""}${user.last_name?.[0] ?? ""}`.toUpperCase() || "A"
    : "DA";

  return (
    <aside
      className={cn(
        "flex h-full flex-col border-r border-border bg-surface-subtle",
        className
      )}
    >
      <div className="flex h-16 items-center gap-2 border-b border-border px-5">
        <div className="flex size-8 items-center justify-center rounded-lg bg-brand-navy text-sm font-bold text-brand-amber">
          A2Z
        </div>
        <div className="min-w-0">
          <p className="truncate text-sm font-bold text-foreground">A2Z Tools</p>
          <p className="truncate text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
            Admin ERP
          </p>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4" aria-label="Admin navigation">
        <ul className="space-y-0.5">
          {visibleNavItems.map((item) => {
            const Icon = iconMap[item.icon];
            const isActive =
              item.href === "/admin-dashboard"
                ? pathname === "/admin-dashboard"
                : pathname.startsWith(item.href);
            const showSection = item.section && item.section !== lastSection;
            if (item.section) lastSection = item.section;

            return (
              <li key={item.href}>
                {showSection ? (
                  <p className="mb-1 mt-4 px-3 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground first:mt-0">
                    {item.section}
                  </p>
                ) : null}
                <Link
                  href={item.href}
                  onClick={onNavigate}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "border-l-[3px] border-brand-amber bg-card pl-[9px] text-foreground shadow-sm"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon className="size-[18px] shrink-0" aria-hidden />
                  <span className="flex-1 truncate">{item.label}</span>
                  {item.badge ? (
                    <Badge variant="warning" className="h-5 min-w-5 justify-center px-1.5 text-[10px]">
                      {item.badge}
                    </Badge>
                  ) : null}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="border-t border-border p-4">
        <div className="flex items-center gap-3 rounded-lg bg-muted/50 p-3">
          <Avatar className="size-9">
            <AvatarFallback className="bg-brand-navy text-xs font-semibold text-brand-amber">
              {initials}
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-foreground">{displayName}</p>
            <p className="truncate text-xs text-muted-foreground">{roleLabel}</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export { AdminSidebar };
