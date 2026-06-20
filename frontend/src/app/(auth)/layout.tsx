import { SiteLayout } from "@/components/layout";

export default function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SiteLayout showFooter={false} showBottomNav={false}>
      {children}
    </SiteLayout>
  );
}
