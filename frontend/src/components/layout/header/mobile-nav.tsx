"use client";

import * as React from "react";
import Link from "next/link";
import {
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Phone,
  Star,
} from "lucide-react";

import {
  megaMenuCategories,
  mobileAccountLinks,
  mobileQuickLinks,
  tradeNavLink,
} from "@/config/navigation";
import { useLayout } from "@/components/layout/layout-provider";
import { SearchBar } from "@/components/layout/search/search-bar";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

type PanelView =
  | { type: "root" }
  | { type: "category"; categoryId: string };

function MobileNav() {
  const { mobileNavOpen, setMobileNavOpen } = useLayout();
  const [panel, setPanel] = React.useState<PanelView>({ type: "root" });

  React.useEffect(() => {
    if (!mobileNavOpen) {
      setPanel({ type: "root" });
    }
  }, [mobileNavOpen]);

  const activeCategory =
    panel.type === "category"
      ? megaMenuCategories.find((category) => category.id === panel.categoryId)
      : null;

  return (
    <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
      <SheetContent
        side="left"
        className="w-[85vw] max-w-[320px] gap-0 p-0 sm:max-w-[320px]"
        aria-label="Navigation menu"
      >
        <SheetHeader className="border-b border-border px-4 py-4 text-left">
          {panel.type === "category" ? (
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label="Back to main menu"
                onClick={() => setPanel({ type: "root" })}
              >
                <ChevronLeft className="size-5" />
              </Button>
              <SheetTitle className="text-base">
                {activeCategory?.label}
              </SheetTitle>
            </div>
          ) : (
            <SheetTitle className="text-base font-normal text-muted-foreground">
              Hello,{" "}
              <Link
                href="/login"
                className="font-semibold text-brand-blue hover:underline"
                onClick={() => setMobileNavOpen(false)}
              >
                Sign in
              </Link>{" "}
              or{" "}
              <Link
                href="/register"
                className="font-semibold text-brand-blue hover:underline"
                onClick={() => setMobileNavOpen(false)}
              >
                Register
              </Link>
            </SheetTitle>
          )}
        </SheetHeader>

        <div className="flex flex-1 flex-col overflow-y-auto">
          {panel.type === "root" ? (
            <>
              <div className="border-b border-border p-4">
                <SearchBar id="drawer-search" showDropdown={false} />
              </div>

              <nav aria-label="Categories" className="flex-1">
                <ul>
                  {megaMenuCategories.map((category) => (
                    <li key={category.id} className="border-b border-border">
                      <button
                        type="button"
                        className="flex min-h-12 w-full items-center justify-between px-4 text-left text-sm font-medium text-brand-navy"
                        onClick={() =>
                          setPanel({ type: "category", categoryId: category.id })
                        }
                      >
                        {category.label}
                        <ChevronRight className="size-4 text-muted-foreground" />
                      </button>
                    </li>
                  ))}
                </ul>
              </nav>

              <div className="border-t border-border bg-brand-amber-light/50 p-4">
                <Link
                  href={tradeNavLink.href}
                  className="flex min-h-11 items-center gap-3 text-sm font-semibold text-brand-navy"
                  onClick={() => setMobileNavOpen(false)}
                >
                  <Star className="size-4 text-brand-amber" />
                  Trade Account
                  <Badge variant="trade" className="ml-auto text-[10px]">
                    B2B
                  </Badge>
                </Link>
                {mobileQuickLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="mt-2 flex min-h-11 items-center gap-3 text-sm text-brand-navy"
                    onClick={() => setMobileNavOpen(false)}
                  >
                    {link.label === "Quick Order" ? (
                      <ClipboardList className="size-4 text-brand-amber" />
                    ) : (
                      <Phone className="size-4 text-brand-amber" />
                    )}
                    {link.label}
                  </Link>
                ))}
              </div>

              <Separator />

              <nav aria-label="Account" className="p-2">
                {mobileAccountLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="flex min-h-11 items-center rounded-md px-3 text-sm text-foreground hover:bg-accent"
                    onClick={() => setMobileNavOpen(false)}
                  >
                    {link.label}
                  </Link>
                ))}
              </nav>
            </>
          ) : activeCategory ? (
            <nav aria-label={activeCategory.label} className="flex-1 p-4">
              {activeCategory.columns.map((column) => (
                <div key={column.title} className="mb-6">
                  <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    {column.title}
                  </h3>
                  <ul className="space-y-1">
                    {column.links.map((link) => (
                      <li key={link.href}>
                        <Link
                          href={link.href}
                          className={cn(
                            "flex min-h-11 items-center rounded-md px-2 text-sm text-foreground hover:bg-accent"
                          )}
                          onClick={() => setMobileNavOpen(false)}
                        >
                          {link.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
              <Link
                href={activeCategory.href}
                className="inline-flex min-h-11 items-center text-sm font-medium text-brand-blue hover:underline"
                onClick={() => setMobileNavOpen(false)}
              >
                View all {activeCategory.label}
              </Link>
            </nav>
          ) : null}
        </div>
      </SheetContent>
    </Sheet>
  );
}

export { MobileNav };
