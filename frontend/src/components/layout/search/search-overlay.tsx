"use client";

import * as React from "react";
import { X } from "lucide-react";

import { useLayout } from "@/components/layout/layout-provider";
import { SearchBar } from "@/components/layout/search/search-bar";
import { Button } from "@/components/ui/button";

function SearchOverlay() {
  const { searchOpen, setSearchOpen } = useLayout();

  React.useEffect(() => {
    if (!searchOpen) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [searchOpen]);

  if (!searchOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Search"
      className="fixed inset-0 z-modal flex flex-col bg-background"
    >
      <div className="relative border-b border-border px-4 py-3">
        <div className="pr-12">
          <SearchBar
            id="mobile-search"
            autoFocus
            onClose={() => setSearchOpen(false)}
          />
        </div>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="absolute right-3 top-3"
          aria-label="Close search"
          onClick={() => setSearchOpen(false)}
        >
          <X className="size-5" />
        </Button>
      </div>

      <p className="px-4 py-3 text-xs text-muted-foreground">
        Arrow keys navigate · Enter to select · Esc to close
      </p>
    </div>
  );
}

export { SearchOverlay };
