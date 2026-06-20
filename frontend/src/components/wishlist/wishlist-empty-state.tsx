import Link from "next/link";
import { ArrowLeft, Heart } from "lucide-react";

import { Container } from "@/components/layout/container";
import { Button } from "@/components/ui/button";

function WishlistEmptyState() {
  return (
    <Container className="flex min-h-[50vh] flex-col items-center justify-center py-16 text-center">
      <div className="flex size-16 items-center justify-center rounded-full bg-brand-blue-light text-brand-blue dark:bg-brand-blue-light/15">
        <Heart className="size-8" aria-hidden />
      </div>
      <h2 className="mt-6 text-2xl font-bold text-foreground">Your wishlist is empty</h2>
      <p className="mt-2 max-w-md text-muted-foreground">
        Save networking, tools, and security products for later — trade pricing is
        shown when available on your account.
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

export { WishlistEmptyState };
