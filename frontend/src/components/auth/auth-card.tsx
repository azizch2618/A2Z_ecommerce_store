import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface AuthCardProps {
  children: ReactNode;
  className?: string;
}

function AuthCard({ children, className }: AuthCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-card p-6 shadow-sm md:p-8",
        className
      )}
    >
      {children}
    </div>
  );
}

export { AuthCard };
