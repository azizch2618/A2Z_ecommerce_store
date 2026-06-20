import { Star } from "lucide-react";

import { cn } from "@/lib/utils";

export interface ProductRatingProps {
  rating: number;
  reviewCount?: number;
  size?: "sm" | "default";
  showCount?: boolean;
  className?: string;
}

function ProductRating({
  rating,
  reviewCount,
  size = "default",
  showCount = true,
  className,
}: ProductRatingProps) {
  const rounded = Math.round(rating * 2) / 2;
  const iconSize = size === "sm" ? "size-3.5" : "size-4";

  return (
    <div
      className={cn("flex flex-wrap items-center gap-1.5", className)}
      aria-label={`${rating} out of 5 stars${reviewCount ? `, ${reviewCount} reviews` : ""}`}
    >
      <div className="flex items-center gap-0.5">
        {Array.from({ length: 5 }).map((_, index) => {
          const fill = rounded >= index + 1 ? "full" : rounded >= index + 0.5 ? "half" : "empty";
          return (
            <Star
              key={index}
              className={cn(
                iconSize,
                fill === "full" && "fill-brand-amber text-brand-amber",
                fill === "half" && "fill-brand-amber/50 text-brand-amber",
                fill === "empty" && "fill-neutral-200 text-neutral-200"
              )}
            />
          );
        })}
      </div>
      <span
        className={cn(
          "font-semibold tabular-nums text-brand-navy",
          size === "sm" ? "text-xs" : "text-sm"
        )}
      >
        {rating.toFixed(1)}
      </span>
      {showCount && reviewCount !== undefined ? (
        <span className={cn("text-muted-foreground", size === "sm" ? "text-xs" : "text-sm")}>
          ({reviewCount})
        </span>
      ) : null}
    </div>
  );
}

export { ProductRating };
