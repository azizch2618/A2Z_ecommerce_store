"use client";

import * as React from "react";

import { RemoteImage } from "@/components/ui/remote-image";
import { cn } from "@/lib/utils";

export interface MediaImageProps {
  src?: string;
  alt?: string;
  label?: string;
  aspectRatio?: "square" | "video" | "wide" | "brand";
  variant?: "default" | "hero" | "product" | "brand" | "category";
  className?: string;
  priority?: boolean;
  sizes?: string;
  overlay?: "none" | "subtle" | "hero" | "bottom";
}

const aspectClasses = {
  square: "aspect-square",
  video: "aspect-video",
  wide: "aspect-[21/9]",
  brand: "aspect-[3/2]",
};

const variantClasses = {
  default:
    "border border-neutral-200/80 bg-gradient-to-br from-neutral-100 via-neutral-50 to-white",
  hero: "border-0 bg-brand-navy shadow-lg",
  product: "border-0 bg-neutral-100",
  brand: "border border-neutral-200/60 bg-neutral-50",
  category: "border-0 bg-neutral-100",
};

const defaultSizes = {
  square: "(max-width: 768px) 50vw, (max-width: 1280px) 33vw, 400px",
  video: "(max-width: 1024px) 100vw, 50vw",
  wide: "100vw",
  brand: "(max-width: 768px) 45vw, 200px",
};

const overlayClasses = {
  none: "",
  subtle:
    "bg-gradient-to-t from-brand-navy/30 via-transparent to-transparent",
  hero: "bg-gradient-to-tr from-brand-navy/70 via-brand-navy/15 to-transparent",
  bottom:
    "bg-gradient-to-t from-brand-navy/80 via-brand-navy/20 to-transparent",
};

function MediaImage({
  src,
  alt,
  label,
  aspectRatio = "square",
  variant = "default",
  className,
  priority = false,
  sizes,
  overlay = "none",
}: MediaImageProps) {
  const resolvedAlt = alt ?? label ?? "Product image";
  const resolvedSizes = sizes ?? defaultSizes[aspectRatio];
  const showOverlay = overlay !== "none" && src;

  if (src) {
    return (
      <div
        className={cn(
          "relative overflow-hidden",
          aspectClasses[aspectRatio],
          variantClasses[variant],
          className
        )}
      >
        <RemoteImage
          src={src}
          alt={resolvedAlt}
          fill
          priority={priority}
          sizes={resolvedSizes}
          className="object-cover"
        />
        {showOverlay ? (
          <div
            className={cn("pointer-events-none absolute inset-0", overlayClasses[overlay])}
            aria-hidden
          />
        ) : null}
      </div>
    );
  }

  const isDark = variant === "hero";

  return (
    <div
      className={cn(
        "relative flex items-center justify-center overflow-hidden text-center",
        aspectClasses[aspectRatio],
        variantClasses[variant],
        className
      )}
      aria-hidden={!label}
    >
      <div
        className={cn(
          "pointer-events-none absolute inset-0 opacity-[0.35]",
          isDark
            ? "bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.15),transparent_50%)]"
            : "bg-[radial-gradient(circle_at_70%_30%,rgba(0,102,204,0.08),transparent_55%)]"
        )}
      />
      {label ? (
        <span
          className={cn(
            "relative z-10 px-4 text-xs font-semibold uppercase tracking-[0.14em]",
            isDark ? "text-white/70" : "text-neutral-500"
          )}
        >
          {label}
        </span>
      ) : null}
    </div>
  );
}

/** @deprecated Use MediaImage — kept for existing imports */
const PlaceholderImage = MediaImage;

export { MediaImage, PlaceholderImage };
