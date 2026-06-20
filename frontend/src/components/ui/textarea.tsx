import * as React from "react";

import { cn } from "@/lib/utils";

const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.ComponentProps<"textarea">
>(({ className, ...props }, ref) => {
  return (
    <textarea
      className={cn(
        "flex min-h-[5.5rem] w-full rounded-md border border-input bg-neutral-50 px-4 py-3 text-base text-foreground transition-normal placeholder:text-muted-foreground focus-visible:border-brand-blue focus-visible:bg-background focus-visible:outline-none focus-visible:shadow-focus-ring disabled:cursor-not-allowed disabled:bg-muted disabled:text-muted-foreground",
        className
      )}
      ref={ref}
      {...props}
    />
  );
});
Textarea.displayName = "Textarea";

export { Textarea };
