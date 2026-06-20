import { Quote, Star } from "lucide-react";

import { testimonials } from "@/config/homepage";
import { Section } from "@/components/layout/section";
import { SectionHeader } from "@/components/home/section-header";
import { Text } from "@/components/ui/typography";

function StarRating() {
  return (
    <div className="flex gap-0.5" aria-label="5 out of 5 stars">
      {Array.from({ length: 5 }).map((_, index) => (
        <Star
          key={index}
          className="size-4 fill-brand-amber text-brand-amber"
          aria-hidden
        />
      ))}
    </div>
  );
}

function TestimonialsSection() {
  return (
    <Section variant="default">
      <SectionHeader
        eyebrow="Customer stories"
        title="Trusted by Australian trades"
        description="Electricians, network installers, and IT teams rely on A2Z for every job — from quote to delivery."
        align="center"
      />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {testimonials.map((item) => (
          <figure
            key={item.id}
            className="group flex h-full flex-col rounded-xl border border-border bg-card p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-brand-blue/20 hover:shadow-lg md:p-7"
          >
            <div className="flex items-center justify-between gap-4">
              <Quote
                className="size-9 text-brand-blue/20 transition-colors group-hover:text-brand-blue/35"
                aria-hidden
              />
              <StarRating />
            </div>
            <blockquote className="mt-5 flex-1 text-sm leading-relaxed text-foreground md:text-[15px] md:leading-7">
              &ldquo;{item.quote}&rdquo;
            </blockquote>
            <figcaption className="mt-6 flex items-center gap-3 border-t border-border pt-5">
              <div
                className="flex size-11 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-brand-blue to-brand-navy text-sm font-bold text-white"
                aria-hidden
              >
                {item.author
                  .split(" ")
                  .map((part) => part[0])
                  .join("")
                  .slice(0, 2)}
              </div>
              <div>
                <p className="font-semibold text-brand-navy">{item.author}</p>
                <Text variant="meta">
                  {item.role}, {item.company}
                </Text>
              </div>
            </figcaption>
          </figure>
        ))}
      </div>
    </Section>
  );
}

export { TestimonialsSection };
