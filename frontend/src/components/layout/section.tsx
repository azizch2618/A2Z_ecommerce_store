import * as React from "react";

import { cn } from "@/lib/utils";
import { Container } from "@/components/layout/container";

export interface SectionProps extends React.HTMLAttributes<HTMLElement> {
  as?: React.ElementType;
  variant?: "default" | "subtle" | "dark";
  containerSize?: React.ComponentProps<typeof Container>["size"];
  contained?: boolean;
}

const variantClasses = {
  default: "bg-background",
  subtle: "bg-surface-subtle",
  dark: "bg-surface-dark text-white",
};

function Section({
  as: Component = "section",
  variant = "default",
  containerSize = "default",
  contained = true,
  className,
  children,
  ...props
}: SectionProps) {
  return (
    <Component
      className={cn(
        "py-12 md:py-16",
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {contained ? (
        <Container size={containerSize}>{children}</Container>
      ) : (
        children
      )}
    </Component>
  );
}

export { Section };
