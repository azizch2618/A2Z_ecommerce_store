import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface CheckoutSectionProps {
  step: number;
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

function CheckoutSection({
  step,
  title,
  description,
  children,
  className,
}: CheckoutSectionProps) {
  return (
    <section
      className={cn(
        "rounded-xl border border-border bg-card p-5 shadow-sm md:p-6",
        className
      )}
    >
      <div className="mb-5 flex items-start gap-3">
        <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-brand-navy text-sm font-bold text-white">
          {step}
        </span>
        <div>
          <h2 className="text-lg font-bold text-brand-navy">{title}</h2>
          {description ? (
            <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>
          ) : null}
        </div>
      </div>
      {children}
    </section>
  );
}

export { CheckoutSection };
