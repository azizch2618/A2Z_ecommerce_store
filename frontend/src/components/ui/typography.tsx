import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const headingVariants = cva("text-foreground tracking-tight", {
  variants: {
    level: {
      h1: "text-3xl font-bold sm:text-4xl lg:text-5xl",
      h2: "text-2xl font-semibold lg:text-3xl",
      h3: "text-xl font-semibold",
      h4: "text-lg font-semibold",
    },
  },
  defaultVariants: {
    level: "h2",
  },
});

type HeadingLevel = "h1" | "h2" | "h3" | "h4";

export interface HeadingProps
  extends React.HTMLAttributes<HTMLHeadingElement>,
    VariantProps<typeof headingVariants> {
  as?: HeadingLevel;
}

function Heading({ className, level, as, ...props }: HeadingProps) {
  const Component = as ?? level ?? "h2";
  return (
    <Component
      className={cn(headingVariants({ level: level ?? (as as HeadingLevel) }), className)}
      {...props}
    />
  );
}

const textVariants = cva("", {
  variants: {
    variant: {
      body: "text-base text-foreground",
      lead: "text-lg text-muted-foreground",
      meta: "text-sm text-muted-foreground",
      caption: "text-xs text-muted-foreground",
      mono: "font-mono text-sm text-muted-foreground",
    },
  },
  defaultVariants: {
    variant: "body",
  },
});

export interface TextProps
  extends React.HTMLAttributes<HTMLParagraphElement>,
    VariantProps<typeof textVariants> {
  as?: "p" | "span" | "div";
}

function Text({ className, variant, as: Component = "p", ...props }: TextProps) {
  return (
    <Component className={cn(textVariants({ variant }), className)} {...props} />
  );
}

export { Heading, Text, headingVariants, textVariants };
