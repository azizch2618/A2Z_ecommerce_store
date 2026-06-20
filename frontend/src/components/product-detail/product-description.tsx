import { Check } from "lucide-react";

import type { ProductDetail } from "@/config/product-detail";
import { cn } from "@/lib/utils";

export interface ProductDescriptionProps {
  product: ProductDetail;
  className?: string;
}

function ProductDescription({ product, className }: ProductDescriptionProps) {
  return (
    <div className={cn("grid gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]", className)}>
      <div>
        <p className="text-base leading-relaxed text-muted-foreground">
          {product.longDescription}
        </p>
        {product.shortDescription !== product.longDescription ? (
          <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
            {product.shortDescription}
          </p>
        ) : null}
      </div>

      <div className="rounded-xl border border-border bg-neutral-50/80 p-5 md:p-6">
        <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-brand-navy">
          Key features
        </h3>
        <ul className="mt-4 space-y-3">
          {product.highlights.map((item) => (
            <li key={item} className="flex items-start gap-3 text-sm">
              <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-brand-blue-light text-brand-blue">
                <Check className="size-3" />
              </span>
              <span className="text-foreground">{item}</span>
            </li>
          ))}
        </ul>

        <dl className="mt-6 space-y-3 border-t border-border pt-6 text-sm">
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Warranty</dt>
            <dd className="text-right font-medium text-brand-navy">{product.warranty}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="text-muted-foreground">Delivery</dt>
            <dd className="text-right font-medium text-brand-navy">{product.deliveryNote}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

export { ProductDescription };
