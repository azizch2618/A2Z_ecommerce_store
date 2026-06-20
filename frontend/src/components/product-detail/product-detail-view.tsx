"use client";

import * as React from "react";
import { toast } from "sonner";

import { useAddToCart } from "@/lib/api/hooks/use-cart";

import type { CategoryProduct } from "@/config/category-page";
import type { ProductDetail } from "@/config/product-detail";
import { getRelatedProducts } from "@/config/product-detail";
import { ProductBrandInfo } from "@/components/product-detail/product-brand-info";
import { ProductGallery } from "@/components/product-detail/product-gallery";
import { ProductPurchasePanel } from "@/components/product-detail/product-purchase-panel";
import { ProductDescription } from "@/components/product-detail/product-description";
import { ProductSpecifications } from "@/components/product-detail/product-specifications";
import { ProductDownloads } from "@/components/product-detail/product-downloads";
import { ProductReviews } from "@/components/product-detail/product-reviews";
import { ProductRelated } from "@/components/product-detail/product-related";
import { ProductMobileBar } from "@/components/product-detail/product-mobile-bar";
import { Container } from "@/components/layout/container";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
import { Section } from "@/components/layout/section";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export interface ProductDetailViewProps {
  product: ProductDetail;
  relatedProducts?: CategoryProduct[];
}

function ProductDetailView({ product, relatedProducts }: ProductDetailViewProps) {
  const related = relatedProducts ?? getRelatedProducts(product);
  const [quantity, setQuantity] = React.useState(1);
  const [activeTab, setActiveTab] = React.useState("description");
  const reviewsRef = React.useRef<HTMLDivElement>(null);

  const canAddToCart = product.stock !== "out_of_stock";
  const maxQty =
    product.stock === "low_stock" && product.stockCount
      ? Math.min(product.stockCount, 99)
      : 99;

  const addToCart = useAddToCart();

  const handleAddToCart = React.useCallback(() => {
    if (!canAddToCart) return;
    if (!product.defaultVariantId) {
      toast.error("Unable to add to cart", { description: "Product variant unavailable." });
      return;
    }
    addToCart.mutate(
      { variant_id: product.defaultVariantId, quantity },
      {
        onSuccess: () => {
          toast.success(`${quantity}× ${product.name} added to cart`, {
            description:
              product.stock === "back_order" ? "Item is on back order" : undefined,
          });
        },
        onError: () => {
          toast.error("Could not add to cart", { description: "Please try again." });
        },
      }
    );
  }, [addToCart, canAddToCart, product.defaultVariantId, product.name, product.stock, quantity]);

  const scrollToReviews = () => {
    setActiveTab("reviews");
    requestAnimationFrame(() => {
      reviewsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  };

  return (
    <div className="pb-28 lg:pb-0">
      <PageBreadcrumbs items={product.breadcrumbs} />

      <Container className="py-6 md:py-10">
        <div className="grid gap-8 lg:grid-cols-2 lg:gap-12 xl:gap-16">
          <ProductGallery
            images={product.images}
            productName={product.name}
            brand={product.brand}
            className="lg:sticky lg:top-24 lg:self-start"
          />
          <div className="space-y-6">
          <ProductPurchasePanel
            product={product}
            quantity={quantity}
            onQuantityChange={setQuantity}
            maxQuantity={maxQty}
            onAddToCart={handleAddToCart}
            onReviewsClick={product.reviews.length > 0 ? scrollToReviews : undefined}
          />

          <ProductBrandInfo brand={product.brand} brandHref={product.brandHref} />
          </div>
        </div>
      </Container>

      <Section className="border-t border-border py-8 md:py-12">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <div className="-mx-1 overflow-x-auto px-1 pb-1">
            <TabsList className="inline-flex h-auto w-full min-w-max justify-start gap-1 rounded-xl bg-neutral-100 p-1.5 lg:w-auto">
              <TabsTrigger
                value="description"
                className="rounded-lg px-4 py-2.5 text-sm data-[state=active]:bg-white data-[state=active]:text-brand-navy data-[state=active]:shadow-sm"
              >
                Description
              </TabsTrigger>
              <TabsTrigger
                value="specifications"
                className="rounded-lg px-4 py-2.5 text-sm data-[state=active]:bg-white data-[state=active]:text-brand-navy data-[state=active]:shadow-sm"
              >
                Specifications
              </TabsTrigger>
              <TabsTrigger
                value="downloads"
                className="rounded-lg px-4 py-2.5 text-sm data-[state=active]:bg-white data-[state=active]:text-brand-navy data-[state=active]:shadow-sm"
              >
                Downloads
              </TabsTrigger>
              <TabsTrigger
                value="reviews"
                className="rounded-lg px-4 py-2.5 text-sm data-[state=active]:bg-white data-[state=active]:text-brand-navy data-[state=active]:shadow-sm"
              >
                Reviews
                {product.reviews.length > 0 ? (
                  <span className="ml-1.5 rounded-full bg-brand-blue-light px-1.5 py-0.5 text-[10px] font-bold text-brand-blue">
                    {product.reviews.length}
                  </span>
                ) : null}
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="description" className="mt-8 focus-visible:outline-none">
            <ProductDescription product={product} />
          </TabsContent>

          <TabsContent value="specifications" className="mt-8 focus-visible:outline-none">
            <ProductSpecifications specifications={product.specifications} />
          </TabsContent>

          <TabsContent value="downloads" className="mt-8 focus-visible:outline-none">
            <ProductDownloads downloads={product.downloads} />
          </TabsContent>

          <TabsContent value="reviews" className="mt-8 focus-visible:outline-none">
            <div ref={reviewsRef}>
              <ProductReviews reviews={product.reviews} />
            </div>
          </TabsContent>
        </Tabs>
      </Section>

      {related.length > 0 ? (
        <Section variant="subtle" className="py-10 md:py-14">
          <div className="mb-8 md:mb-10">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-brand-blue">
              Frequently bought together
            </p>
            <h2 className="mt-2 text-xl font-bold text-brand-navy md:text-2xl">
              Related products
            </h2>
          </div>
          <ProductRelated products={related} />
        </Section>
      ) : null}

      <ProductMobileBar
        product={product}
        quantity={quantity}
        onQuantityChange={setQuantity}
        maxQuantity={maxQty}
        onAddToCart={handleAddToCart}
      />
    </div>
  );
}

export { ProductDetailView };
