import Link from "next/link";
import { ArrowRight, FileText, Users } from "lucide-react";

import { tradeCtaContent } from "@/config/homepage";
import { Container } from "@/components/layout/container";
import { Heading, Text } from "@/components/ui/typography";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

function TradeCtaSection() {
  return (
    <section className="relative overflow-hidden bg-brand-navy text-white">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(217,119,6,0.18),transparent_55%)]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.03] [background-image:linear-gradient(rgba(255,255,255,0.5)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.5)_1px,transparent_1px)] [background-size:40px_40px]"
        aria-hidden
      />

      <Container className="relative grid gap-10 py-14 md:py-18 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:gap-14">
        <div className="space-y-6">
          <Badge
            variant="trade"
            className="border-brand-amber/40 bg-brand-amber/15 text-brand-amber"
          >
            Trade & B2B
          </Badge>
          <Heading level="h2" as="h2" className="max-w-xl text-white">
            {tradeCtaContent.title}
          </Heading>
          <Text variant="lead" className="max-w-2xl text-neutral-300">
            {tradeCtaContent.description}
          </Text>

          <ul className="grid gap-3 sm:grid-cols-2">
            <li className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm text-neutral-200">
              <Users className="size-5 shrink-0 text-brand-amber" aria-hidden />
              Net 30 terms for qualified accounts
            </li>
            <li className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm text-neutral-200">
              <FileText className="size-5 shrink-0 text-brand-amber" aria-hidden />
              Bulk ordering & price lists
            </li>
          </ul>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Button asChild size="lg" className="w-full sm:w-auto">
              <Link href={tradeCtaContent.primaryCta.href}>
                {tradeCtaContent.primaryCta.label}
                <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button
              asChild
              size="lg"
              variant="secondary"
              className="w-full border-white/20 bg-white/10 text-white hover:bg-white/15 sm:w-auto"
            >
              <Link href={tradeCtaContent.secondaryCta.href}>
                {tradeCtaContent.secondaryCta.label}
              </Link>
            </Button>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-white/10 to-white/5 p-6 shadow-2xl backdrop-blur-sm md:p-8">
          <p className="text-center text-xs font-semibold uppercase tracking-[0.16em] text-brand-amber">
            Trusted by Australian trade
          </p>
          <div className="mt-6 grid grid-cols-3 gap-4 divide-x divide-white/10">
            {tradeCtaContent.stats.map((stat) => (
              <div key={stat.label} className="px-2 text-center first:pl-0 last:pr-0">
                <p className="text-2xl font-bold tracking-tight text-white md:text-4xl">
                  {stat.value}
                </p>
                <p className="mt-2 text-xs leading-snug text-neutral-400 md:text-sm">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </Container>
    </section>
  );
}

export { TradeCtaSection };
