import Link from "next/link";
import {
  ArrowRight,
  Building2,
  HardHat,
  Network,
  Shield,
  Wrench,
  Zap,
} from "lucide-react";

import { categoryTiles } from "@/config/homepage";
import { getCategoryImage } from "@/config/visual-assets";
import { Section } from "@/components/layout/section";
import { SectionHeader } from "@/components/home/section-header";
import { PlaceholderImage } from "@/components/home/placeholder-image";
import { Text } from "@/components/ui/typography";
import { cn } from "@/lib/utils";

const categoryIcons = {
  networking: Network,
  tools: Wrench,
  electrical: Zap,
  security: Shield,
  brands: Building2,
  trade: HardHat,
} as const;

function CategoriesSection() {
  return (
    <Section variant="default" className="relative">
      <SectionHeader
        eyebrow="Browse"
        title="Shop by category"
        description="Networking, tools, electrical, and security — curated for Australian trade professionals and IT installers."
        href="/networking"
        linkLabel="Explore all categories"
      />

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6 lg:gap-5">
        {categoryTiles.map((category) => {
          const Icon =
            categoryIcons[category.id as keyof typeof categoryIcons] ?? Network;
          const isTrade = category.id === "trade";

          return (
            <Link
              key={category.id}
              href={category.href}
              className={cn(
                "group relative flex flex-col overflow-hidden rounded-xl border bg-card shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg",
                isTrade
                  ? "border-brand-amber/30 hover:border-brand-amber/50"
                  : "border-border hover:border-brand-blue/30"
              )}
            >
              <div className="relative">
                <PlaceholderImage
                  src={getCategoryImage(category.id).src}
                  alt={getCategoryImage(category.id).alt}
                  aspectRatio="square"
                  variant="category"
                  overlay="subtle"
                  className="rounded-none"
                />
                <div className="absolute left-3 top-3 flex size-10 items-center justify-center rounded-lg bg-white/90 text-brand-blue shadow-sm backdrop-blur-sm transition-colors group-hover:bg-brand-blue group-hover:text-white">
                  <Icon className="size-5" aria-hidden />
                </div>
              </div>
              <div className="flex flex-1 flex-col p-4">
                <h3 className="text-sm font-semibold text-brand-navy transition-colors group-hover:text-brand-blue md:text-base">
                  {category.label}
                </h3>
                <Text variant="meta" className="mt-1 line-clamp-2">
                  {category.description}
                </Text>
                <span className="mt-auto flex items-center gap-1 pt-3 text-xs font-semibold text-brand-blue">
                  {category.productCount}
                  <ArrowRight className="size-3.5 transition-transform group-hover:translate-x-1" />
                </span>
              </div>
            </Link>
          );
        })}
      </div>
    </Section>
  );
}

export { CategoriesSection };
