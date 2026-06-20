export type {
  AccountDashboardStats,
  AccountOrder,
  SavedAddress,
  SavedQuote,
} from "@/types/account";

export const accountNavItems = [
  { label: "Dashboard", href: "/account", icon: "layout-dashboard" as const },
  { label: "Orders", href: "/account/orders", icon: "package" as const },
  { label: "Wishlist", href: "/account/wishlist", icon: "heart" as const },
  { label: "Saved Addresses", href: "/account/addresses", icon: "map-pin" as const },
  { label: "Trade Account", href: "/account/trade", icon: "building-2" as const },
  { label: "Account Settings", href: "/account/settings", icon: "settings" as const },
] as const;

export function getAccountBreadcrumbs(section: string) {
  return [
    { label: "Home", href: "/" },
    { label: "My account", href: "/account" },
    { label: section },
  ];
}
