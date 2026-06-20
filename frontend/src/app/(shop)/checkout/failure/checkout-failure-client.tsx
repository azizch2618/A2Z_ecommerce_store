"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { XCircle } from "lucide-react";

import { Container } from "@/components/layout/container";
import { Button } from "@/components/ui/button";
import { useOrder } from "@/lib/api/hooks/use-orders";

export default function CheckoutFailurePage() {
  const searchParams = useSearchParams();
  const orderId = searchParams.get("order_id") ?? "";
  const { data: order } = useOrder(orderId, { enabled: Boolean(orderId) });

  return (
    <Container className="py-16">
      <div className="mx-auto max-w-lg text-center">
        <XCircle className="mx-auto size-14 text-destructive" />
        <h1 className="mt-6 text-2xl font-bold text-brand-navy">Payment failed</h1>
        <p className="mt-2 text-muted-foreground">
          {order
            ? `We couldn't process payment for order ${order.order_number}. No charge was completed.`
            : "We couldn't process your payment. Please try again."}
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Button asChild>
            <Link href="/checkout">Return to checkout</Link>
          </Button>
          {orderId ? (
            <Button variant="outline" asChild>
              <Link href={`/account/orders/${orderId}`}>View order</Link>
            </Button>
          ) : null}
        </div>
      </div>
    </Container>
  );
}
