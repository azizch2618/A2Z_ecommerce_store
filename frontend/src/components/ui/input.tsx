import * as React from "react";

import { cn } from "@/lib/utils";

const Input = React.forwardRef<HTMLInputElement, React.ComponentProps<"input">>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-11 w-full rounded-md border border-input bg-neutral-50 px-4 py-3 text-base text-foreground transition-normal file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:border-brand-blue focus-visible:bg-background focus-visible:outline-none focus-visible:shadow-focus-ring disabled:cursor-not-allowed disabled:bg-muted disabled:text-muted-foreground",
          "aria-[invalid=true]:border-error aria-[invalid=true]:focus-visible:shadow-[0_0_0_3px_rgb(220_38_38/0.25)]",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };
