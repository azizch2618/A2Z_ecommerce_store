"use client";

import * as React from "react";
import Link from "next/link";
import { ChevronDown } from "lucide-react";

import {
  megaMenuCategories,
  tradeNavLink,
  type MegaMenuCategory,
} from "@/config/navigation";
import { MegaMenu } from "@/components/layout/header/mega-menu";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

function CategoryNav() {
  const [activeCategory, setActiveCategory] =
    React.useState<MegaMenuCategory | null>(null);
  const closeTimerRef = React.useRef<number | null>(null);

  const openCategory = (category: MegaMenuCategory) => {
    if (closeTimerRef.current) {
      window.clearTimeout(closeTimerRef.current);
      closeTimerRef.current = null;
    }
    setActiveCategory(category);
  };

  const scheduleClose = () => {
    closeTimerRef.current = window.setTimeout(() => {
      setActiveCategory(null);
    }, 300);
  };

  const closeMenu = () => {
    if (closeTimerRef.current) {
      window.clearTimeout(closeTimerRef.current);
    }
    setActiveCategory(null);
  };

  return (
    <nav
      className="relative hidden border-t border-border bg-background lg:block"
      aria-label="Product categories"
      onMouseLeave={scheduleClose}
    >
      <div className="container-app">
        <ul className="flex h-11 items-center gap-1">
          {megaMenuCategories.map((category) => {
            const isActive = activeCategory?.id === category.id;

            return (
              <li
                key={category.id}
                className="h-full"
                onMouseEnter={() => openCategory(category)}
              >
                <Link
                  href={category.href}
                  className={cn(
                    "inline-flex h-11 items-center gap-1 px-4 text-sm font-medium transition-colors",
                    isActive
                      ? "text-brand-blue"
                      : "text-brand-navy hover:text-brand-blue"
                  )}
                  aria-expanded={isActive}
                  aria-haspopup="true"
                  onFocus={() => openCategory(category)}
                >
                  {category.label}
                  <ChevronDown
                    className={cn(
                      "size-4 transition-transform",
                      isActive && "rotate-180"
                    )}
                    aria-hidden
                  />
                </Link>
              </li>
            );
          })}

          <li className="ml-auto h-full">
            <Link
              href={tradeNavLink.href}
              className="inline-flex h-11 items-center gap-2 px-4 text-sm font-semibold text-brand-navy transition-colors hover:text-brand-amber"
            >
              <Badge variant="trade" className="px-1.5 py-0 text-[10px]">
                Trade
              </Badge>
              {tradeNavLink.label}
            </Link>
          </li>
        </ul>
      </div>

      {activeCategory ? (
        <MegaMenu
          category={activeCategory}
          open={Boolean(activeCategory)}
          onClose={closeMenu}
        />
      ) : null}
    </nav>
  );
}

export { CategoryNav };
