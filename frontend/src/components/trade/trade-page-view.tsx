import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
import { Container } from "@/components/layout/container";
import { TradeCtaSection } from "@/components/home/trade-cta-section";
import { WhyChooseUsSection } from "@/components/home/why-choose-us-section";
import { tradeCtaContent } from "@/config/homepage";

function TradePageView() {
  return (
    <>
      <PageBreadcrumbs
        items={[
          { label: "Home", href: "/" },
          { label: "Trade Account" },
        ]}
      />
      <TradeCtaSection />
      <Container className="py-10 md:py-14">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-2xl font-bold text-brand-navy md:text-3xl">
            Australian trade & B2B accounts
          </h1>
          <p className="mt-3 text-base leading-relaxed text-muted-foreground">
            {tradeCtaContent.description}
          </p>
        </div>
      </Container>
      <WhyChooseUsSection />
    </>
  );
}

export { TradePageView };
