import { SiteLayout } from "@/components/layout";
import { TradePageView } from "@/components/trade/trade-page-view";

export const metadata = {
  title: "Trade Account | A2Z Tools",
  description:
    "Open an A2Z Tools trade account for Net 30 terms, bulk ordering, project pricing, and dedicated Australian support.",
};

export default function TradePage() {
  return (
    <SiteLayout>
      <TradePageView />
    </SiteLayout>
  );
}
