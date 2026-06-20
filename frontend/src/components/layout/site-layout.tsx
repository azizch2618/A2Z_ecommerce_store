"use client";

import * as React from "react";

import { cn } from "@/lib/utils";
import { useCart } from "@/lib/api/hooks/use-cart";
import { LayoutProvider } from "@/components/layout/layout-provider";
import { SkipLink } from "@/components/layout/skip-link";
import { TopAnnouncementBar } from "@/components/layout/top-announcement-bar";
import { SiteHeader } from "@/components/layout/header/site-header";
import { SiteFooter } from "@/components/layout/site-footer";
import { MobileBottomNav } from "@/components/layout/header/mobile-bottom-nav";
import { SearchOverlay } from "@/components/layout/search/search-overlay";
import { CompareProvider } from "@/components/compare";
import { WishlistProvider, useWishlist } from "@/components/wishlist";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Toaster } from "@/components/ui/sonner";

export interface SiteLayoutProps {
  children: React.ReactNode;
  className?: string;
  showAnnouncement?: boolean;
  showHeader?: boolean;
  showFooter?: boolean;
  showBottomNav?: boolean;
  cartCount?: number;
}

function SiteLayoutContent({
  children,
  className,
  showAnnouncement = true,
  showHeader = true,
  showFooter = true,
  showBottomNav = true,
  cartCount: cartCountProp,
}: SiteLayoutProps) {
  const { count: wishlistCount } = useWishlist();
  const { data: cart } = useCart();
  const cartCount = cartCountProp ?? cart?.item_count ?? 0;

  return (
    <TooltipProvider delayDuration={200}>
      <div className={cn("relative flex min-h-screen flex-col", className)}>
        <SkipLink />
        {showAnnouncement ? <TopAnnouncementBar /> : null}
        {showHeader ? (
          <SiteHeader cartCount={cartCount} wishlistCount={wishlistCount} />
        ) : null}
        <main
          id="main-content"
          className={cn(
            "flex-1 focus:outline-none",
            showBottomNav && "pb-14 lg:pb-0"
          )}
          tabIndex={-1}
        >
          {children}
        </main>
        {showFooter ? <SiteFooter /> : null}
        {showBottomNav ? <MobileBottomNav cartCount={cartCount} /> : null}
        <SearchOverlay />
        <Toaster position="top-center" richColors closeButton />
      </div>
    </TooltipProvider>
  );
}

function SiteLayout(props: SiteLayoutProps) {
  return (
    <LayoutProvider>
      <CompareProvider>
        <WishlistProvider>
          <SiteLayoutContent {...props} />
        </WishlistProvider>
      </CompareProvider>
    </LayoutProvider>
  );
}

export { SiteLayout };
