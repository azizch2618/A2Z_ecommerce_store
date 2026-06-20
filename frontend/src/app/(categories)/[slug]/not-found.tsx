import Link from "next/link";

import { SiteLayout } from "@/components/layout";
import { Container } from "@/components/layout/container";
import { Button } from "@/components/ui/button";

export default function CategoryNotFound() {
  return (
    <SiteLayout>
      <Container className="flex min-h-[50vh] flex-col items-center justify-center py-16 text-center">
        <h1 className="text-2xl font-bold text-brand-navy">Category not found</h1>
        <p className="mt-2 max-w-md text-muted-foreground">
          That category doesn&apos;t exist or may have moved. Browse our main departments
          below.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Button asChild>
            <Link href="/networking">Networking</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/products">All products</Link>
          </Button>
        </div>
      </Container>
    </SiteLayout>
  );
}
