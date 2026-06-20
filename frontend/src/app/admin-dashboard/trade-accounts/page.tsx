import type { Metadata } from "next";

import { TradeAccountsPageView } from "@/components/admin/pages/trade-accounts-page-view";

export const metadata: Metadata = { title: "Trade Accounts | Admin | A2Z Tools" };

export default function AdminTradeAccountsPage() {
  return <TradeAccountsPageView />;
}
