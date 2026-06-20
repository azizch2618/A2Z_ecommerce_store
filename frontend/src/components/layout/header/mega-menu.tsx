"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowRight, ChevronRight } from "lucide-react";

import type { MegaMenuCategory } from "@/config/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export interface MegaMenuProps {
  category: MegaMenuCategory;
  open: boolean;
  onClose: () => void;
}

function MegaMenu({ category, open, onClose }: MegaMenuProps) {
  const panelRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (!open) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      ref={panelRef}
      role="region"
      aria-label={`${category.label} menu`}
      className="absolute left-0 right-0 top-full z-dropdown border-b border-border bg-background shadow-lg"
      onMouseLeave={onClose}
    >
      <div className="container-app py-8">
        <div
          className={cn(
            "grid gap-8",
            category.featured
              ? "lg:grid-cols-[1fr_1fr_1fr_280px]"
              : "lg:grid-cols-3"
          )}
        >
          {category.columns.map((column) => (
            <div key={column.title}>
              <h3 className="mb-4 text-sm font-semibold text-brand-navy">
                {column.title}
              </h3>
              <ul className="space-y-2.5">
                {column.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-sm text-muted-foreground transition-colors hover:text-brand-blue"
                      onClick={onClose}
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {category.featured ? (
            <div className="rounded-lg border border-border bg-surface-subtle p-5">
              <p className="text-xs font-semibold uppercase tracking-wider text-brand-blue">
                Featured
              </p>
              <p className="mt-2 text-sm font-medium text-muted-foreground">
                {category.featured.brand}
              </p>
              <h4 className="mt-1 text-lg font-semibold text-brand-navy">
                {category.featured.title}
              </h4>
              <p className="mt-2 text-sm text-muted-foreground">
                {category.featured.description}
              </p>
              <Button asChild variant="ghost" className="mt-4 h-auto px-0">
                <Link href={category.featured.href} onClick={onClose}>
                  Shop now
                  <ArrowRight className="size-4" />
                </Link>
              </Button>
            </div>
          ) : null}
        </div>

        <div className="mt-6 border-t border-border pt-4">
          <Link
            href={category.href}
            className="inline-flex items-center gap-1 text-sm font-medium text-brand-blue hover:underline"
            onClick={onClose}
          >
            View all {category.label}
            <ChevronRight className="size-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}

export { MegaMenu };
