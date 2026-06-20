"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  LayoutGrid,
  Search,
  ShoppingCart,
  User,
} from "lucide-react";

import { useLayout } from "@/components/layout/layout-provider";
import { cn } from "@/lib/utils";

export interface MobileBottomNavProps {
  cartCount?: number;
  hiddenOnPaths?: string[];
}

const navItems = [
  { label: "Home", href: "/", icon: Home },
  { label: "Shop", href: "/networking", icon: LayoutGrid },
  { label: "Search", href: "#search", icon: Search, action: "search" as const },
  { label: "Cart", href: "/cart", icon: ShoppingCart },
  { label: "Account", href: "/account", icon: User },
];

function MobileBottomNav({
  cartCount = 0,
  hiddenOnPaths = ["/checkout"],
}: MobileBottomNavProps) {
  const pathname = usePathname();
  const { setSearchOpen } = useLayout();

  const hidden = hiddenOnPaths.some((path) => pathname.startsWith(path));
  if (hidden) return null;

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-bottom-nav border-t border-border bg-background pb-[env(safe-area-inset-bottom)] lg:hidden"
      aria-label="Mobile bottom navigation"
    >
      <ul className="grid h-14 grid-cols-5">
        {navItems.map((item) => {
          const isSearch = item.action === "search";
          const isActive =
            !isSearch &&
            (item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href));

          const content = (
            <>
              <span className="relative">
                <item.icon
                  className={cn(
                    "size-5",
                    isActive ? "text-brand-blue" : "text-muted-foreground"
                  )}
                  aria-hidden
                />
                {item.label === "Cart" && cartCount > 0 ? (
                  <span className="absolute -right-2 -top-2 flex size-4 items-center justify-center rounded-full bg-error text-[9px] font-semibold text-white">
                    {cartCount > 9 ? "9+" : cartCount}
                  </span>
                ) : null}
              </span>
              <span
                className={cn(
                  "text-[10px] font-medium",
                  isActive ? "text-brand-blue" : "text-muted-foreground"
                )}
              >
                {item.label}
              </span>
            </>
          );

          return (
            <li key={item.label}>
              {isSearch ? (
                <button
                  type="button"
                  className="flex h-full w-full flex-col items-center justify-center gap-1"
                  aria-label="Open search"
                  onClick={() => setSearchOpen(true)}
                >
                  {content}
                </button>
              ) : (
                <Link
                  href={item.href}
                  className="flex h-full w-full flex-col items-center justify-center gap-1"
                  aria-current={isActive ? "page" : undefined}
                  aria-label={
                    item.label === "Cart" && cartCount > 0
                      ? `Cart, ${cartCount} items`
                      : item.label
                  }
                >
                  {content}
                </Link>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export { MobileBottomNav };
