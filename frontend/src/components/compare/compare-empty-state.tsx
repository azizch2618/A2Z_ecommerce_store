import Link from "next/link";
import { ArrowLeft, GitCompareArrows } from "lucide-react";

import { MIN_COMPARE_PRODUCTS } from "@/config/compare";
import { Container } from "@/components/layout/container";
import { Button } from "@/components/ui/button";

function CompareEmptyState() {
  return (
    <Container className="flex min-h-[50vh] flex-col items-center justify-center py-16 text-center">
      <div className="flex size-16 items-center justify-center rounded-full bg-brand-blue-light text-brand-blue dark:bg-brand-blue-light/15">
        <GitCompareArrows className="size-8" aria-hidden />
      </div>
      <h2 className="mt-6 text-2xl font-bold text-foreground">Nothing to compare yet</h2>
      <p className="mt-2 max-w-md text-muted-foreground">
        Add {MIN_COMPARE_PRODUCTS}–4 networking products to compare specifications,
        trade pricing, and stock side by side.
      </p>
      <Button asChild className="mt-8 gap-2" size="lg">
        <Link href="/networking">
          <ArrowLeft className="size-4" />
          Browse networking
        </Link>
      </Button>
    </Container>
  );
}

export { CompareEmptyState };
