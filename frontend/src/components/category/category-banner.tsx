import Link from "next/link";
import type { Route } from "next";
import { ArrowRight, Package } from "lucide-react";

import { RemoteImage } from "@/components/ui/remote-image";

import type { CategoryPageData } from "@/config/category-page";
import { getCategoryImage } from "@/config/visual-assets";
import { Container } from "@/components/layout/container";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export interface CategoryBannerProps {
  category: CategoryPageData;
  className?: string;
}

function CategoryBanner({ category, className }: CategoryBannerProps) {
  const bannerImage = getCategoryImage(category.slug);

  return (
    <section
      className={cn(
        "relative overflow-hidden border-b border-brand-navy/20 text-white",
        className
      )}
    >
      <div className="pointer-events-none absolute inset-0" aria-hidden>
        <RemoteImage
          src={bannerImage.src}
          alt=""
          fill
          priority
          sizes="100vw"
          className="object-cover object-center"
        />
        <div className="absolute inset-0 bg-brand-navy/88 lg:bg-gradient-to-r lg:from-brand-navy lg:via-brand-navy/92 lg:to-brand-navy/55" />
        <div
          className="absolute inset-0 opacity-[0.06]"
          style={{
            backgroundImage:
              "linear-gradient(to right, #fff 1px, transparent 1px), linear-gradient(to bottom, #fff 1px, transparent 1px)",
            backgroundSize: "48px 48px",
          }}
        />
      </div>

      <div
        className="pointer-events-none absolute -right-24 -top-24 size-96 rounded-full bg-brand-blue/15 blur-3xl"
        aria-hidden
      />

      <Container className="relative py-10 md:py-14">
        <div className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl space-y-4">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-blue-light">
              {category.eyebrow}
            </p>
            <h1 className="text-3xl font-bold tracking-tight md:text-4xl lg:text-5xl">
              {category.title}
            </h1>
            <p className="text-base leading-relaxed text-white/85 md:text-lg">
              {category.description}
            </p>
            <div className="flex flex-wrap items-center gap-3 pt-1">
              <Badge
                variant="secondary"
                className="gap-1.5 border-white/10 bg-white/10 text-white hover:bg-white/10"
              >
                <Package className="size-3.5" />
                {category.productCountLabel}
              </Badge>
              <span className="text-sm text-white/65">
                Free delivery over $150 · Trade pricing available
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-6 lg:max-w-md lg:items-end">
            <div className="relative hidden w-full max-w-sm overflow-hidden rounded-xl border border-white/15 shadow-2xl lg:block">
              <div className="relative aspect-[4/3]">
                <RemoteImage
                  src={bannerImage.src}
                  alt={bannerImage.alt}
                  fill
                  sizes="(max-width: 1024px) 0px, 400px"
                  className="object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-brand-navy/80 via-transparent to-transparent" />
                <p className="absolute bottom-3 left-3 right-3 text-xs font-medium leading-snug text-white/90">
                  {bannerImage.alt}
                </p>
              </div>
            </div>

            {category.subcategories.length > 0 ? (
              <nav
                aria-label={`${category.title} subcategories`}
                className="flex flex-wrap gap-2 lg:justify-end"
              >
                {category.subcategories.map((sub) => (
                  <Link
                    key={sub.href}
                    href={sub.href as Route}
                    className="inline-flex items-center gap-1 rounded-full border border-white/15 bg-white/5 px-3.5 py-1.5 text-sm font-medium text-white/90 backdrop-blur-sm transition-colors hover:border-brand-blue/40 hover:bg-brand-blue/20 hover:text-white"
                  >
                    {sub.label}
                    <ArrowRight className="size-3.5 opacity-60" />
                  </Link>
                ))}
              </nav>
            ) : null}
          </div>
        </div>
      </Container>
    </section>
  );
}

export { CategoryBanner };
