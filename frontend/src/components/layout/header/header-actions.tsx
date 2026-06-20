"use client";

import Link from "next/link";
import {
  Heart,
  Search,
  ShoppingCart,
  User,
} from "lucide-react";

import { useLayout } from "@/components/layout/layout-provider";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export interface HeaderActionsProps {
  className?: string;
  cartCount?: number;
  wishlistCount?: number;
  showSearchButton?: boolean;
}

function ActionBadge({ count }: { count: number }) {
  if (count <= 0) return null;

  return (
    <span className="absolute -right-1 -top-1 flex size-5 items-center justify-center rounded-full bg-error text-[10px] font-semibold text-white">
      {count > 9 ? "9+" : count}
    </span>
  );
}

function HeaderActions({
  className,
  cartCount = 0,
  wishlistCount = 0,
  showSearchButton = false,
}: HeaderActionsProps) {
  const { setSearchOpen } = useLayout();

  return (
    <div className={cn("flex items-center gap-1 sm:gap-2", className)}>
      {showSearchButton ? (
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="lg:hidden"
          aria-label="Open search"
          onClick={() => setSearchOpen(true)}
        >
          <Search className="size-5" />
        </Button>
      ) : null}

      <Button
        asChild
        variant="ghost"
        size="icon"
        className="hidden sm:inline-flex"
        aria-label={`Wishlist${wishlistCount ? `, ${wishlistCount} items` : ""}`}
      >
        <Link href="/wishlist" className="relative">
          <Heart className="size-5" />
          <ActionBadge count={wishlistCount} />
        </Link>
      </Button>

      <Button
        asChild
        variant="ghost"
        size="icon"
        aria-label={`Cart${cartCount ? `, ${cartCount} items` : ""}`}
      >
        <Link href="/cart" className="relative">
          <ShoppingCart className="size-5" />
          <ActionBadge count={cartCount} />
        </Link>
      </Button>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            className="hidden sm:inline-flex"
            aria-label="Account menu"
          >
            <User className="size-5" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-52">
          <DropdownMenuLabel>Account</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <Link href="/login">Sign in</Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link href="/register">Create account</Link>
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <Link href="/trade">Trade account</Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link href="/account">Dashboard</Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link href="/account/orders">My orders</Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link href="/wishlist">Wishlist</Link>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}

export { HeaderActions };
