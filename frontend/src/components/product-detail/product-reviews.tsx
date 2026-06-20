"use client";

import { Star } from "lucide-react";

import type { ProductReview } from "@/config/product-detail";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

export interface ProductReviewsProps {
  reviews: ProductReview[];
  className?: string;
}

function StarRating({ rating, size = "default" }: { rating: number; size?: "sm" | "default" }) {
  return (
    <div className="flex items-center gap-0.5" aria-label={`${rating} out of 5 stars`}>
      {Array.from({ length: 5 }).map((_, index) => (
        <Star
          key={index}
          className={cn(
            size === "sm" ? "size-3.5" : "size-4",
            index < rating
              ? "fill-brand-amber text-brand-amber"
              : "fill-neutral-200 text-neutral-200"
          )}
        />
      ))}
    </div>
  );
}

function formatReviewDate(date: string) {
  return new Date(date).toLocaleDateString("en-AU", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function ProductReviews({ reviews, className }: ProductReviewsProps) {
  if (reviews.length === 0) {
    return (
      <div className="rounded-xl border border-dashed border-border bg-neutral-50 px-6 py-12 text-center">
        <p className="font-medium text-brand-navy">No reviews yet</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Be the first to review this product after purchase.
        </p>
      </div>
    );
  }

  const average =
    reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length;
  const distribution = [5, 4, 3, 2, 1].map((stars) => ({
    stars,
    count: reviews.filter((r) => r.rating === stars).length,
    percent: (reviews.filter((r) => r.rating === stars).length / reviews.length) * 100,
  }));

  return (
    <div className={cn("grid gap-8 lg:grid-cols-[280px_minmax(0,1fr)]", className)}>
      <div className="rounded-xl border border-border bg-neutral-50/80 p-6">
        <p className="text-4xl font-bold text-brand-navy">{average.toFixed(1)}</p>
        <StarRating rating={Math.round(average)} />
        <p className="mt-2 text-sm text-muted-foreground">
          Based on {reviews.length} verified review{reviews.length !== 1 ? "s" : ""}
        </p>

        <div className="mt-6 space-y-2">
          {distribution.map((row) => (
            <div key={row.stars} className="flex items-center gap-2 text-xs">
              <span className="w-3 tabular-nums text-muted-foreground">{row.stars}</span>
              <Star className="size-3 fill-brand-amber text-brand-amber" />
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-neutral-200">
                <div
                  className="h-full rounded-full bg-brand-amber transition-all"
                  style={{ width: `${row.percent}%` }}
                />
              </div>
              <span className="w-6 text-right tabular-nums text-muted-foreground">
                {row.count}
              </span>
            </div>
          ))}
        </div>
      </div>

      <ul className="space-y-4">
        {reviews.map((review) => (
          <li
            key={review.id}
            className="rounded-xl border border-border bg-card p-5 md:p-6"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <StarRating rating={review.rating} size="sm" />
                <h4 className="mt-2 font-semibold text-brand-navy">{review.title}</h4>
              </div>
              {review.verified ? (
                <Badge variant="success" className="shrink-0 text-[10px] uppercase">
                  Verified purchase
                </Badge>
              ) : null}
            </div>

            <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
              {review.body}
            </p>

            <p className="mt-4 text-xs text-muted-foreground">
              <span className="font-medium text-foreground">{review.author}</span>
              {" · "}
              {review.role}, {review.company}
              {" · "}
              {formatReviewDate(review.date)}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export { ProductReviews };
