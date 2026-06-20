import * as React from "react";

import { cn } from "@/lib/utils";

export interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  as?: React.ElementType;
  size?: "default" | "narrow" | "wide" | "full";
}

const sizeClasses = {
  default: "max-w-content",
  narrow: "max-w-3xl",
  wide: "max-w-screen-2xl",
  full: "max-w-none",
};

function Container({
  as: Component = "div",
  size = "default",
  className,
  ...props
}: ContainerProps) {
  return (
    <Component
      className={cn("container-app", sizeClasses[size], className)}
      {...props}
    />
  );
}

export { Container };
