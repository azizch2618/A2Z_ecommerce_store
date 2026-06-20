import * as React from "react";

import { cn } from "@/lib/utils";

export interface GridProps extends React.HTMLAttributes<HTMLDivElement> {
  cols?: 1 | 2 | 3 | 4 | 6 | 12;
  gap?: "sm" | "md" | "lg";
}

const colClasses = {
  1: "grid-cols-1",
  2: "grid-cols-1 sm:grid-cols-2",
  3: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3",
  4: "grid-cols-2 lg:grid-cols-4",
  6: "grid-cols-2 md:grid-cols-3 lg:grid-cols-6",
  12: "grid-cols-4 md:grid-cols-8 lg:grid-cols-12",
};

const gapClasses = {
  sm: "gap-4",
  md: "gap-6",
  lg: "gap-8",
};

function Grid({
  cols = 2,
  gap = "md",
  className,
  ...props
}: GridProps) {
  return (
    <div
      className={cn("grid", colClasses[cols], gapClasses[gap], className)}
      {...props}
    />
  );
}

export { Grid };
