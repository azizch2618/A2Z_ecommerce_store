import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export interface AdminCardProps {
  title: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  contentClassName?: string;
}

function AdminCard({
  title,
  description,
  action,
  children,
  className,
  contentClassName,
}: AdminCardProps) {
  return (
    <section
      className={cn(
        "rounded-xl border border-border bg-card shadow-sm",
        className
      )}
    >
      <div className="flex items-start justify-between gap-4 border-b border-border px-5 py-4">
        <div>
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          {description ? (
            <p className="mt-0.5 text-sm text-muted-foreground">{description}</p>
          ) : null}
        </div>
        {action}
      </div>
      <div className={cn("p-5", contentClassName)}>{children}</div>
    </section>
  );
}

export { AdminCard };
