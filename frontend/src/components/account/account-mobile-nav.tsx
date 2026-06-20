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
import { cn } from "@/lib/utils";

const iconMap = {
  "layout-dashboard": LayoutDashboard,
  package: Package,
  heart: Heart,
  "map-pin": MapPin,
  "building-2": Building2,
  settings: Settings,
} as const;

function AccountMobileNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Account navigation"
      className="mb-6 -mx-1 overflow-x-auto px-1 lg:hidden"
    >
      <ul className="flex min-w-max gap-2 pb-1">
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
                  "inline-flex items-center gap-2 rounded-full border px-3.5 py-2 text-xs font-medium whitespace-nowrap transition-colors",
                  isActive
                    ? "border-brand-blue bg-brand-blue-light text-brand-blue dark:bg-brand-blue-light/15"
                    : "border-border bg-card text-muted-foreground hover:text-foreground"
                )}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon className="size-3.5" aria-hidden />
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export { AccountMobileNav };
