import Link from "next/link";
import { MIN_COMPARE_PRODUCTS } from "@/config/compare";
import { Container } from "@/components/layout/container";
import { Button } from "@/components/ui/button";

function CompareInsufficientState() {
  return (
    <Container className="flex min-h-[40vh] flex-col items-center justify-center py-12 text-center">
      <h2 className="text-xl font-bold text-foreground">Add another product</h2>
      <p className="mt-2 max-w-md text-sm text-muted-foreground">
        Select at least {MIN_COMPARE_PRODUCTS} products to run a side-by-side
        comparison. Add one more from the networking catalogue.
      </p>
      <Button asChild className="mt-6" variant="outline">
        <Link href="/networking">Browse networking products</Link>
      </Button>
    </Container>
  );
}

export { CompareInsufficientState };
