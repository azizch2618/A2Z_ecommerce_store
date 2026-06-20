import Link from "next/link";
import { ArrowRight, Check, MapPin } from "lucide-react";

import { heroContent } from "@/config/homepage";
import { visualAssets } from "@/config/visual-assets";
import { Container } from "@/components/layout/container";
import { PlaceholderImage } from "@/components/home/placeholder-image";
import { Heading, Text } from "@/components/ui/typography";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

function HeroSection() {
  return (
    <section className="relative overflow-hidden border-b border-border bg-brand-navy">
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(0,102,204,0.25),transparent_55%)]"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.04] [background-image:linear-gradient(rgba(255,255,255,0.6)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.6)_1px,transparent_1px)] [background-size:48px_48px]"
        aria-hidden
      />

      <Container className="relative grid gap-10 py-12 md:py-16 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:gap-14 xl:py-20">
        <div className="space-y-7 text-white">
          <div className="flex flex-wrap items-center gap-3">
            <Badge
              variant="trade"
              className="border-brand-amber/30 bg-brand-amber/15 text-brand-amber"
            >
              {heroContent.eyebrow}
            </Badge>
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-neutral-300">
              <MapPin className="size-3.5 text-brand-amber" aria-hidden />
              Australian owned · GST registered
            </span>
          </div>

          <Heading level="h1" as="h1" className="max-w-xl text-white">
            {heroContent.title}
          </Heading>
          <Text variant="lead" className="max-w-lg text-neutral-300">
            {heroContent.description}
          </Text>

          <ul className="grid gap-3 sm:grid-cols-3">
            {heroContent.highlights.map((item) => (
              <li
                key={item}
                className="flex items-start gap-2.5 rounded-lg border border-white/10 bg-white/5 px-3 py-2.5 text-sm text-neutral-200"
              >
                <Check
                  className="mt-0.5 size-4 shrink-0 text-brand-amber"
                  aria-hidden
                />
                <span>{item}</span>
              </li>
            ))}
          </ul>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <Button asChild size="lg" className="w-full sm:w-auto">
              <Link href={heroContent.primaryCta.href}>
                {heroContent.primaryCta.label}
                <ArrowRight className="size-4" />
              </Link>
            </Button>
            <Button
              asChild
              variant="secondary"
              size="lg"
              className="w-full border-white/20 bg-white/10 text-white hover:bg-white/15 sm:w-auto"
            >
              <Link href={heroContent.secondaryCta.href}>
                {heroContent.secondaryCta.label}
              </Link>
            </Button>
          </div>
        </div>

        <div className="relative">
          <div
            className="absolute -inset-3 rounded-2xl bg-brand-blue/20 blur-2xl"
            aria-hidden
          />
          <div className="relative overflow-hidden rounded-2xl border border-white/10 shadow-2xl">
            <PlaceholderImage
              src={visualAssets.hero.src}
              alt={visualAssets.hero.alt}
              aspectRatio="video"
              variant="hero"
              overlay="hero"
              priority
              className="w-full rounded-none lg:aspect-[4/3]"
            />
            <div className="absolute bottom-0 left-0 right-0 border-t border-white/10 bg-brand-navy/90 p-4 backdrop-blur-sm md:p-5">
              <p className="text-xs font-semibold uppercase tracking-wider text-brand-amber">
                Featured range
              </p>
              <p className="mt-1 text-sm font-medium text-white md:text-base">
                Cisco · Ubiquiti · TP-Link Omada
              </p>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}

export { HeroSection };
