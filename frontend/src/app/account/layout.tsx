import { SiteLayout } from "@/components/layout";
import { RouteGuard } from "@/components/rbac/route-guard";

export default function AccountLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SiteLayout>
      <RouteGuard>{children}</RouteGuard>
    </SiteLayout>
  );
}
