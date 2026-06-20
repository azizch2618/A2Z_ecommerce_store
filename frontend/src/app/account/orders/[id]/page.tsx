import { AccountOrderDetailPageView } from "@/components/account/account-order-detail-page-view";

export const metadata = {
  title: "Order details | A2Z Tools",
  description: "View your A2Z Tools order details.",
};

interface AccountOrderDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function AccountOrderDetailPage({
  params,
}: AccountOrderDetailPageProps) {
  const { id } = await params;
  return <AccountOrderDetailPageView orderId={id} />;
}
