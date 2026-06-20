import Link from "next/link";

import { cn } from "@/lib/utils";

function SkipLink({ className }: { className?: string }) {
  return (
    <Link
      href="#main-content"
      className={cn(
        "sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-max",
        "rounded-md bg-brand-blue px-4 py-2 text-sm font-medium text-white",
        "focus:shadow-focus-ring",
        className
      )}
    >
      Skip to main content
    </Link>
  );
}

export { SkipLink };
