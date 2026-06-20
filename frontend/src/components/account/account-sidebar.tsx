"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Building2,
  Heart,
  LayoutDashboard,
  MapPin,
  Package,
  Settings,
} from "lucide-react";

import { accountNavItems } from "@/config/account";
import { useCurrentUser } from "@/lib/api/hooks/use-auth";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

const iconMap = {
  "layout-dashboard": LayoutDashboard,
  package: Package,
  heart: Heart,
  "map-pin": MapPin,
  "building-2": Building2,
  settings: Settings,
} as const;

export interface AccountSidebarProps {
  className?: string;
}

function AccountSidebar({ className }: AccountSidebarProps) {
  const pathname = usePathname();
  const { data: user } = useCurrentUser();
  const firstName = user?.first_name ?? "";
  const lastName = user?.last_name ?? "";
  const initials = `${firstName[0] ?? ""}${lastName[0] ?? ""}` || "AT";
  const company =
    user?.organization?.trading_name ?? user?.organization?.legal_name ?? "";
  const isTrade = user?.customer?.customer_type === "trade";

  return (
    <aside
      className={cn(
        "rounded-xl border border-border bg-card p-4 shadow-sm lg:sticky lg:top-24",
        className
      )}
    >
      <div className="mb-5 flex items-center gap-3 border-b border-border pb-5">
        <Avatar className="size-11">
          <AvatarFallback className="bg-brand-blue text-sm font-semibold text-white">
            {initials}
          </AvatarFallback>
        </Avatar>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-foreground">
            {firstName} {lastName}
          </p>
          <p className="truncate text-xs text-muted-foreground">{company}</p>
          {isTrade ? (
            <Badge className="mt-1.5 bg-brand-blue text-[10px] text-white hover:bg-brand-blue">
              Trade account
            </Badge>
          ) : null}
        </div>
      </div>

      <nav aria-label="Account navigation">
        <ul className="space-y-1">
          {accountNavItems.map((item) => {
            const Icon = iconMap[item.icon];
            const isActive =
              item.href === "/account"
                ? pathname === "/account"
                : pathname.startsWith(item.href);

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-brand-blue-light text-brand-blue dark:bg-brand-blue-light/15 dark:text-brand-blue"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon className="size-4 shrink-0" aria-hidden />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}

export { AccountSidebar };
