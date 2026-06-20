import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";

interface SpinnerProps {
  className?: string;
  label?: string;
}

function Spinner({ className, label = "Loading" }: SpinnerProps) {
  return (
    <Loader2
      className={cn("size-5 animate-spin text-brand-blue", className)}
      role="status"
      aria-label={label}
    />
  );
}

export { Spinner };
