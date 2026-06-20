"use client";

import { Menu } from "lucide-react";

import { useLayout } from "@/components/layout/layout-provider";
import { CategoryNav } from "@/components/layout/header/category-nav";
import { HeaderActions } from "@/components/layout/header/header-actions";
import { MobileNav } from "@/components/layout/header/mobile-nav";
import { SiteLogo } from "@/components/layout/header/site-logo";
import { SearchBar } from "@/components/layout/search/search-bar";
import { Container } from "@/components/layout/container";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

export interface SiteHeaderProps {
  cartCount?: number;
  wishlistCount?: number;
  className?: string;
}

function SiteHeader({
  cartCount = 0,
  wishlistCount = 0,
  className,
}: SiteHeaderProps) {
  const { setMobileNavOpen, headerScrolled } = useLayout();

  return (
    <>
      <header
        className={cn(
          "sticky top-0 z-sticky bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80",
          headerScrolled ? "shadow-sm" : "border-b border-border",
          className
        )}
      >
        <Container className="flex h-14 items-center gap-3 md:h-[4.5rem] md:gap-4">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="lg:hidden"
            aria-label="Open navigation menu"
            onClick={() => setMobileNavOpen(true)}
          >
            <Menu className="size-5" />
          </Button>

          <SiteLogo compact className="lg:hidden" />
          <SiteLogo className="hidden lg:inline-flex" />

          <div className="hidden flex-1 justify-center px-4 lg:flex">
            <SearchBar className="max-w-[30rem] xl:max-w-[32rem]" />
          </div>

          <HeaderActions
            cartCount={cartCount}
            wishlistCount={wishlistCount}
            showSearchButton
            className="ml-auto"
          />
        </Container>

        <CategoryNav />
      </header>

      <MobileNav />
    </>
  );
}

export { SiteHeader };
