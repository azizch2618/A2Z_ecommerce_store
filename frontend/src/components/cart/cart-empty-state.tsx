import Link from "next/link";
import { ArrowLeft, ShoppingBag } from "lucide-react";

import { Container } from "@/components/layout/container";
import { Button } from "@/components/ui/button";

function CartEmptyState() {
  return (
    <Container className="flex min-h-[50vh] flex-col items-center justify-center py-16 text-center">
      <div className="flex size-16 items-center justify-center rounded-full bg-brand-blue-light text-brand-blue">
        <ShoppingBag className="size-8" />
      </div>
      <h1 className="mt-6 text-2xl font-bold text-brand-navy">Your cart is empty</h1>
      <p className="mt-2 max-w-md text-muted-foreground">
        Browse our catalogue of networking, security, and test equipment — Australian
        stock with GST-inclusive pricing.
      </p>
      <Button asChild className="mt-8 gap-2" size="lg">
        <Link href="/products">
          <ArrowLeft className="size-4" />
          Continue shopping
        </Link>
      </Button>
    </Container>
  );
}

export { CartEmptyState };
