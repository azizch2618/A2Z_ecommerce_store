import type { ReactNode } from "react";

import { AccountMobileNav } from "@/components/account/account-mobile-nav";
import { AccountSidebar } from "@/components/account/account-sidebar";
import { Container } from "@/components/layout/container";
import { cn } from "@/lib/utils";

export interface AccountShellProps {
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

function AccountShell({ title, description, children, className }: AccountShellProps) {
  return (
    <Container className={cn("py-8 md:py-10", className)}>
      <div className="mb-6 md:mb-8">
        <h1 className="text-2xl font-bold text-foreground md:text-3xl">{title}</h1>
        {description ? (
          <p className="mt-1 text-sm text-muted-foreground">{description}</p>
        ) : null}
      </div>

      <AccountMobileNav />

      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)] xl:grid-cols-[260px_minmax(0,1fr)]">
        <AccountSidebar className="hidden lg:block" />
        <div>{children}</div>
      </div>
    </Container>
  );
}

export { AccountShell };
