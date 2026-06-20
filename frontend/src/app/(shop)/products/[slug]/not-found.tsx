import Link from "next/link";

import { Container } from "@/components/layout/container";
import { Button } from "@/components/ui/button";

export default function ProductNotFound() {
  return (
    <Container className="flex min-h-[50vh] flex-col items-center justify-center py-16 text-center">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-brand-blue">
        404
      </p>
      <h1 className="mt-2 text-2xl font-bold text-brand-navy">Product not found</h1>
      <p className="mt-2 max-w-md text-muted-foreground">
        This product may have been discontinued or the link is incorrect.
      </p>
      <div className="mt-8 flex flex-wrap justify-center gap-3">
        <Button asChild>
          <Link href="/products">Browse all products</Link>
        </Button>
        <Button asChild variant="outline">
          <Link href="/networking">Networking category</Link>
        </Button>
      </div>
    </Container>
  );
}
