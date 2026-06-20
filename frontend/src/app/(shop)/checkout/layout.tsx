import { SiteLayout } from "@/components/layout";
import { RouteGuard } from "@/components/rbac/route-guard";

export default function CheckoutLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SiteLayout>
      <RouteGuard requireVerified>{children}</RouteGuard>
    </SiteLayout>
  );
}
