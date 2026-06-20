import { Suspense } from "react";

import { ProductListingPageView } from "@/components/shop";

export const metadata = {
  title: "All Products | A2Z Tools",
  description:
    "Browse networking, security, and test equipment from Cisco, Ubiquiti, TP-Link Omada, Fluke Networks, and Hikvision. Australian stock with GST-inclusive pricing.",
};

function ProductListingFallback() {
  return (
    <div className="flex min-h-[40vh] items-center justify-center">
      <p className="text-sm text-muted-foreground">Loading products…</p>
    </div>
  );
}

export default function ProductsListingPage() {
  return (
    <Suspense fallback={<ProductListingFallback />}>
      <ProductListingPageView />
    </Suspense>
  );
}
