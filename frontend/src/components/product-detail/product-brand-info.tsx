import Link from "next/link";
import { BadgeCheck, ExternalLink } from "lucide-react";

import { getBrandProfile } from "@/config/brand-profiles";
import { brandIdFromLabel } from "@/config/category-page";
import { BrandLogo } from "@/components/product/brand-logo";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export interface ProductBrandInfoProps {
  brand: string;
  brandHref: string;
  className?: string;
}

function ProductBrandInfo({ brand, brandHref, className }: ProductBrandInfoProps) {
  const profile = getBrandProfile(brand);
  const brandId = brandIdFromLabel(brand);

  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-card p-4 shadow-sm md:p-5",
        className
      )}
    >
      <div className="flex items-start gap-3">
        <BrandLogo brandId={brandId} brandName={brand} size="md" className="size-11" />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <Link
              href={brandHref}
              className="text-sm font-semibold text-brand-navy transition-colors hover:text-brand-blue"
            >
              {profile.name}
            </Link>
            {profile.authorised ? (
              <Badge
                variant="outline"
                className="gap-1 border-success/30 bg-success-light/50 text-[10px] font-semibold uppercase tracking-wide text-success"
              >
                <BadgeCheck className="size-3" />
                Authorised reseller
              </Badge>
            ) : null}
          </div>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            {profile.description}
          </p>
          <Link
            href={profile.href}
            className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-brand-blue hover:underline"
          >
            View all {profile.name} products
            <ExternalLink className="size-3" />
          </Link>
        </div>
      </div>
    </div>
  );
}

export { ProductBrandInfo };
