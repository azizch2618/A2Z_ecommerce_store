import { CheckCircle2, Headphones, Truck } from "lucide-react";

import type { CategoryPageData } from "@/config/category-page";
import { Container } from "@/components/layout/container";
import { cn } from "@/lib/utils";

export interface CategoryDescriptionProps {
  category: CategoryPageData;
  className?: string;
}

const trustPoints = [
  {
    icon: CheckCircle2,
    title: "Authorised distributor",
    description: "Genuine stock with full manufacturer warranty",
  },
  {
    icon: Truck,
    title: "Australia-wide delivery",
    description: "Free shipping on orders over $150",
  },
  {
    icon: Headphones,
    title: "Local technical support",
    description: "Pre-sales and post-sales help from our team",
  },
];

function CategoryDescription({ category, className }: CategoryDescriptionProps) {
  return (
    <section className={cn("border-b border-border py-8 md:py-10", className)}>
      <Container>
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)] lg:gap-12">
          <div>
            <h2 className="text-lg font-bold text-brand-navy md:text-xl">
              About {category.title}
            </h2>
            <p className="mt-4 text-base leading-relaxed text-muted-foreground">
              {category.longDescription}
            </p>
          </div>

          <ul className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            {trustPoints.map((point) => (
              <li
                key={point.title}
                className="flex items-start gap-3 rounded-xl border border-border bg-card p-4"
              >
                <point.icon className="mt-0.5 size-5 shrink-0 text-brand-blue" />
                <div>
                  <p className="text-sm font-semibold text-brand-navy">{point.title}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">
                    {point.description}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </Container>
    </section>
  );
}

export { CategoryDescription };
