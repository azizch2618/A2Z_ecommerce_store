import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { featuredBrands } from "@/config/homepage";
import { getBrandImage } from "@/config/visual-assets";
import { Section } from "@/components/layout/section";
import { SectionHeader } from "@/components/home/section-header";
import { PlaceholderImage } from "@/components/home/placeholder-image";
import { Text } from "@/components/ui/typography";

function FeaturedBrandsSection() {
  return (
    <Section variant="default">
      <SectionHeader
        eyebrow="Authorised stock"
        title="Featured brands"
        description="Cisco, Ubiquiti, Fluke, and more — the manufacturers you specify on every job."
        href="/brands"
        linkLabel="View all brands"
      />

      <div className="flex gap-4 overflow-x-auto pb-3 [-ms-overflow-style:none] [scrollbar-width:none] md:grid md:grid-cols-3 md:overflow-visible lg:grid-cols-6 lg:gap-5 [&::-webkit-scrollbar]:hidden">
        {featuredBrands.map((brand) => (
          <Link
            key={brand.id}
            href={brand.href}
            className="group relative min-w-[11rem] flex-shrink-0 overflow-hidden rounded-xl border border-border bg-card p-4 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-brand-blue/25 hover:shadow-md md:min-w-0"
          >
            <div className="mb-4 overflow-hidden rounded-lg">
              <PlaceholderImage
                src={getBrandImage(brand.id).src}
                alt={getBrandImage(brand.id).alt}
                aspectRatio="brand"
                variant="brand"
                className="transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <div className="flex items-start justify-between gap-2">
              <div>
                <h3 className="text-sm font-semibold text-brand-navy transition-colors group-hover:text-brand-blue">
                  {brand.name}
                </h3>
                <Text variant="meta" className="mt-1 line-clamp-2">
                  {brand.description}
                </Text>
              </div>
              <ArrowUpRight
                className="size-4 shrink-0 text-muted-foreground transition-all group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-brand-blue"
                aria-hidden
              />
            </div>
          </Link>
        ))}
      </div>
    </Section>
  );
}

export { FeaturedBrandsSection };
