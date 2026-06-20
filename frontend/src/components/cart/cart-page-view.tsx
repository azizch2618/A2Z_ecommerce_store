"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";
import { toast } from "sonner";

import { cartPageBreadcrumbs } from "@/config/cart-page";
import { calculateCartSummary } from "@/lib/cart";
import { useCart, useRemoveCartItem, useUpdateCartItem } from "@/lib/api/hooks/use-cart";
import { mapApiCartToUiItems } from "@/lib/api/mappers/cart-mapper";
import { CartEmptyState } from "@/components/cart/cart-empty-state";
import { CartLineItem } from "@/components/cart/cart-line-item";
import { CartMobileBar } from "@/components/cart/cart-mobile-bar";
import { CartOrderSummary } from "@/components/cart/cart-order-summary";
import { CartTrustRow } from "@/components/cart/cart-trust-row";
import { Container } from "@/components/layout/container";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

function CartPageView() {
  const { data: cart, isLoading, isError } = useCart();
  const updateItem = useUpdateCartItem();
  const removeItem = useRemoveCartItem();

  const items = React.useMemo(
    () => (cart ? mapApiCartToUiItems(cart) : []),
    [cart]
  );

  const summary = React.useMemo(() => calculateCartSummary(items), [items]);

  const updateQuantity = (id: string, quantity: number) => {
    updateItem.mutate(
      { itemId: id, payload: { quantity } },
      {
        onError: () => toast.error("Could not update quantity"),
      }
    );
  };

  const handleRemove = (id: string) => {
    const removed = items.find((item) => item.id === id);
    removeItem.mutate(id, {
      onSuccess: () => {
        if (removed) toast.info(`${removed.name} removed from cart`);
      },
      onError: () => toast.error("Could not remove item"),
    });
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-brand-blue" />
      </div>
    );
  }

  if (isError) {
    return (
      <Container className="py-16 text-center">
        <p className="text-muted-foreground">Unable to load cart. Is the API running?</p>
      </Container>
    );
  }

  if (items.length === 0) {
    return (
      <>
        <PageBreadcrumbs items={cartPageBreadcrumbs} />
        <CartEmptyState />
      </>
    );
  }

  return (
    <>
      <PageBreadcrumbs items={cartPageBreadcrumbs} />

      <Container className="pb-28 pt-8 md:pb-10 md:pt-10 lg:pb-10">
        <div className="mb-6 flex flex-col gap-4 sm:mb-8 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-2xl font-bold text-brand-navy md:text-3xl">
                Shopping cart
              </h1>
              <Badge
                variant="secondary"
                className="bg-brand-blue-light font-semibold text-brand-navy"
              >
                {summary.itemCount} {summary.itemCount === 1 ? "item" : "items"}
              </Badge>
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Review quantities and pricing before checkout. Australian GST included
              on all lines.
            </p>
          </div>
          <Button asChild variant="outline" className="gap-2 self-start sm:self-auto">
            <Link href="/products">
              <ArrowLeft className="size-4" />
              Continue shopping
            </Link>
          </Button>
        </div>

        <div className="grid gap-8 lg:grid-cols-[1fr_360px] lg:gap-10">
          <div className="space-y-4">
            {items.map((item) => (
              <CartLineItem
                key={item.id}
                item={item}
                onQuantityChange={updateQuantity}
                onRemove={handleRemove}
              />
            ))}
            <CartTrustRow />
          </div>

          <CartOrderSummary summary={summary} />
        </div>
      </Container>

      <CartMobileBar summary={summary} />
    </>
  );
}

export { CartPageView };
