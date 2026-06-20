import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { cn } from "@/lib/utils";
import { Heading, Text } from "@/components/ui/typography";
import { Button } from "@/components/ui/button";

export interface SectionHeaderProps {
  title: string;
  description?: string;
  href?: string;
  linkLabel?: string;
  className?: string;
  align?: "left" | "center";
  eyebrow?: string;
}

function SectionHeader({
  title,
  description,
  href,
  linkLabel = "View all",
  className,
  align = "left",
  eyebrow,
}: SectionHeaderProps) {
  const centered = align === "center";

  return (
    <div
      className={cn(
        "mb-8 md:mb-12",
        centered ? "text-center" : "",
        className
      )}
    >
      <div
        className={cn(
          "flex flex-col gap-4",
          centered
            ? "items-center"
            : "sm:flex-row sm:items-end sm:justify-between"
        )}
      >
        <div className={cn("space-y-3", centered && "max-w-2xl")}>
          {eyebrow ? (
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-blue">
              {eyebrow}
            </p>
          ) : null}
          <Heading level="h2" as="h2" className="text-brand-navy">
            {title}
          </Heading>
          {description ? (
            <Text variant="lead" className={cn(centered && "mx-auto")}>
              {description}
            </Text>
          ) : null}
        </div>
        {href ? (
          <Button
            asChild
            variant="ghost"
            className={cn(
              "shrink-0 text-brand-blue hover:bg-brand-blue-light",
              centered && "mt-1"
            )}
          >
            <Link href={href}>
              {linkLabel}
              <ArrowRight className="size-4" />
            </Link>
          </Button>
        ) : null}
      </div>
      <div
        className={cn(
          "mt-6 h-px w-full bg-gradient-to-r from-transparent via-border to-transparent",
          centered && "max-w-xs mx-auto"
        )}
        aria-hidden
      />
    </div>
  );
}

export { SectionHeader };
