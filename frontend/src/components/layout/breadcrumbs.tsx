import * as React from "react";

import { cn } from "@/lib/utils";
import { Container } from "@/components/layout/container";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";

export interface BreadcrumbItemData {
  label: string;
  href?: string;
}

export interface PageBreadcrumbsProps extends React.HTMLAttributes<HTMLElement> {
  items: BreadcrumbItemData[];
}

function PageBreadcrumbs({ items, className, ...props }: PageBreadcrumbsProps) {
  if (items.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className={cn("border-b border-border bg-background", className)} {...props}>
      <Container className="flex min-h-10 items-center py-2">
        <Breadcrumb>
          <BreadcrumbList>
            {items.map((item, index) => {
              const isLast = index === items.length - 1;
              return (
                <React.Fragment key={`${item.label}-${index}`}>
                  <BreadcrumbItem>
                    {isLast || !item.href ? (
                      <BreadcrumbPage>{item.label}</BreadcrumbPage>
                    ) : (
                      <BreadcrumbLink href={item.href}>{item.label}</BreadcrumbLink>
                    )}
                  </BreadcrumbItem>
                  {!isLast ? <BreadcrumbSeparator /> : null}
                </React.Fragment>
              );
            })}
          </BreadcrumbList>
        </Breadcrumb>
      </Container>
    </nav>
  );
}

export { PageBreadcrumbs };
