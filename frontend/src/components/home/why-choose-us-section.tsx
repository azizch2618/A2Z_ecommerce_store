import {
  Headphones,
  PackageCheck,
  ShieldCheck,
  Truck,
} from "lucide-react";

import { valueProps } from "@/config/homepage";
import { Section } from "@/components/layout/section";
import { SectionHeader } from "@/components/home/section-header";
import { Text } from "@/components/ui/typography";
import { cn } from "@/lib/utils";

const icons = [PackageCheck, ShieldCheck, Headphones, Truck];

const accentColors = [
  "from-brand-blue/10 to-brand-blue-light/50 text-brand-blue",
  "from-success/10 to-success-light/50 text-success",
  "from-brand-amber/10 to-brand-amber-light/50 text-brand-amber",
  "from-brand-navy/10 to-neutral-100 text-brand-navy",
];

function WhyChooseUsSection() {
  return (
    <Section variant="subtle">
      <SectionHeader
        eyebrow="The A2Z difference"
        title="Why choose A2Z Tools"
        description="Enterprise-grade selection, trade-friendly service, and Australian support — without the enterprise hassle."
        align="center"
      />

      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4 lg:gap-6">
        {valueProps.map((item, index) => {
          const Icon = icons[index] ?? PackageCheck;

          return (
            <div
              key={item.id}
              className="group relative overflow-hidden rounded-xl border border-border bg-card p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
            >
              <span
                className="absolute right-4 top-4 text-4xl font-bold leading-none text-neutral-100 transition-colors group-hover:text-brand-blue-light"
                aria-hidden
              >
                {String(index + 1).padStart(2, "0")}
              </span>
              <div
                className={cn(
                  "mb-5 flex size-12 items-center justify-center rounded-xl bg-gradient-to-br",
                  accentColors[index]
                )}
              >
                <Icon className="size-5" aria-hidden />
              </div>
              <h3 className="text-lg font-semibold text-brand-navy">
                {item.title}
              </h3>
              <Text variant="meta" className="mt-2 leading-relaxed">
                {item.description}
              </Text>
            </div>
          );
        })}
      </div>
    </Section>
  );
}

export { WhyChooseUsSection };
