import { Package } from "lucide-react";

import type { CategoryPageData } from "@/config/category-page";
import { Container } from "@/components/layout/container";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export interface ListingPageHeaderProps {
  page: CategoryPageData;
  productCount: number;
  className?: string;
}

function ListingPageHeader({ page, productCount, className }: ListingPageHeaderProps) {
  return (
    <section
      className={cn(
        "border-b border-border bg-gradient-to-b from-neutral-50 to-background",
        className
      )}
    >
      <Container className="py-8 md:py-10">
        <div className="max-w-3xl space-y-4">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-brand-blue">
            {page.eyebrow}
          </p>
          <h1 className="text-3xl font-bold tracking-tight text-brand-navy md:text-4xl">
            {page.title}
          </h1>
          <p className="text-base leading-relaxed text-muted-foreground md:text-lg">
            {page.description}
          </p>
          <div className="flex flex-wrap items-center gap-3 pt-1">
            <Badge
              variant="secondary"
              className="gap-1.5 border-brand-blue/20 bg-brand-blue-light/50 text-brand-navy"
            >
              <Package className="size-3.5 text-brand-blue" />
              {productCount} products
            </Badge>
            <span className="text-sm text-muted-foreground">
              Free delivery over $150 · Trade pricing available
            </span>
          </div>
        </div>
      </Container>
    </section>
  );
}

export { ListingPageHeader };
