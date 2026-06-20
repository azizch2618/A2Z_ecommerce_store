"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { compareBreadcrumbs, MAX_COMPARE_PRODUCTS } from "@/config/compare";
import { useCompare } from "@/components/compare/compare-provider";
import { CompareEmptyState } from "@/components/compare/compare-empty-state";
import { CompareInsufficientState } from "@/components/compare/compare-insufficient-state";
import { CompareMobileCards } from "@/components/compare/compare-mobile-cards";
import { CompareTable } from "@/components/compare/compare-table";
import { Container } from "@/components/layout/container";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

function ComparePageView() {
  const { count, canCompare } = useCompare();

  if (count === 0) {
    return (
      <>
        <PageBreadcrumbs items={compareBreadcrumbs} />
        <CompareEmptyState />
      </>
    );
  }

  if (!canCompare) {
    return (
      <>
        <PageBreadcrumbs items={compareBreadcrumbs} />
        <Container className="py-8 md:py-10">
          <CompareInsufficientState />
          <CompareMobileCards />
        </Container>
      </>
    );
  }

  return (
    <>
      <PageBreadcrumbs items={compareBreadcrumbs} />

      <Container className="py-8 md:py-10">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-bold text-foreground md:text-3xl">
                Compare products
              </h1>
              <Badge
                variant="secondary"
                className="bg-brand-blue-light font-semibold text-brand-navy dark:text-foreground"
              >
                {count} of {MAX_COMPARE_PRODUCTS}
              </Badge>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Side-by-side networking hardware comparison — prices include Australian GST.
            </p>
          </div>
          <Button asChild variant="outline" className="gap-2 self-start sm:self-auto">
            <Link href="/networking">
              <ArrowLeft className="size-4" />
              Continue shopping
            </Link>
          </Button>
        </div>

        <CompareTable />
        <CompareMobileCards />
      </Container>
    </>
  );
}

export { ComparePageView };
