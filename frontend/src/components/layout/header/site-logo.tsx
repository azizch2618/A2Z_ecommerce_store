import Image from "next/image";
import Link from "next/link";

import {
  brand,
  LOGO_MAX_WIDTH_PX,
  LOGOMARK_SIZE_PX,
} from "@/config/brand";
import { cn } from "@/lib/utils";

export interface SiteLogoProps {
  className?: string;
  /** @deprecated Both variants use the official lockup; kept for API compatibility */
  variant?: "default" | "reversed";
  /** Show logomark only (mobile header) */
  compact?: boolean;
}

function SiteLogo({
  className,
  variant: _variant = "default",
  compact = false,
}: SiteLogoProps) {
  const { full, mark } = brand.logo;

  return (
    <Link
      href="/"
      className={cn("inline-flex shrink-0 items-center", className)}
      aria-label={`${brand.name} — Home`}
    >
      {compact ? (
        <span
          className="relative overflow-hidden rounded-md bg-black"
          style={{
            width: LOGOMARK_SIZE_PX,
            height: LOGOMARK_SIZE_PX,
          }}
        >
          <Image
            src={mark.src}
            alt={mark.alt}
            width={mark.width}
            height={mark.height}
            className="absolute left-1/2 top-0 h-auto w-[220%] max-w-none -translate-x-1/2 object-cover object-top"
            sizes={`${LOGOMARK_SIZE_PX}px`}
            priority
          />
        </span>
      ) : (
        <Image
          src={full.src}
          alt={full.alt}
          width={full.width}
          height={full.height}
          className="h-9 w-auto max-w-[7.5rem] rounded-md object-contain sm:h-10 sm:max-w-[8.75rem] md:max-w-[140px]"
          sizes={`(max-width: 768px) 120px, ${LOGO_MAX_WIDTH_PX}px`}
          priority
        />
      )}
    </Link>
  );
}

export { SiteLogo };
