import { RouteGuard } from "@/components/rbac/route-guard";

export default function WishlistLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <RouteGuard redirectTo="/login">{children}</RouteGuard>;
}
