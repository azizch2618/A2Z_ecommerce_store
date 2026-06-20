"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { CheckCircle2, Loader2 } from "lucide-react";

import { Container } from "@/components/layout/container";
import { Button } from "@/components/ui/button";
import { useOrder } from "@/lib/api/hooks/use-orders";
import { formatAud } from "@/lib/cart";

export default function CheckoutSuccessPage() {
  const searchParams = useSearchParams();
  const orderId = searchParams.get("order_id") ?? "";
  const { data: order, isLoading, refetch } = useOrder(orderId, {
    enabled: Boolean(orderId),
  });

  React.useEffect(() => {
    if (!orderId) return;
    if (order?.payment_status === "paid") return;

    const interval = setInterval(() => {
      void refetch();
    }, 2000);
    return () => clearInterval(interval);
  }, [orderId, order?.payment_status, refetch]);

  const isPaid = order?.payment_status === "paid" || order?.status === "paid";
  const isAwaiting = order?.status === "awaiting_payment";

  return (
    <Container className="py-16">
      <div className="mx-auto max-w-lg text-center">
        {isLoading && !order ? (
          <Loader2 className="mx-auto size-12 animate-spin text-brand-blue" />
        ) : (
          <>
            <CheckCircle2
              className={`mx-auto size-14 ${isPaid ? "text-success" : "text-brand-blue"}`}
            />
            <h1 className="mt-6 text-2xl font-bold text-brand-navy">
              {isPaid ? "Payment successful" : "Payment processing"}
            </h1>
            {order ? (
              <p className="mt-2 text-muted-foreground">
                Order {order.order_number}
                {isPaid
                  ? ` — ${formatAud(order.total_inc_gst_cents / 100)} AUD inc GST`
                  : isAwaiting
                    ? " — confirming your payment with our payment provider."
                    : " — we're finalising your order."}
              </p>
            ) : (
              <p className="mt-2 text-muted-foreground">
                Thank you. Your order confirmation will appear shortly.
              </p>
            )}
            {!isPaid && order ? (
              <p className="mt-4 flex items-center justify-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="size-4 animate-spin" />
                Waiting for payment confirmation…
              </p>
            ) : null}
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
              {orderId ? (
                <Button asChild>
                  <Link href={`/account/orders/${orderId}`}>View order</Link>
                </Button>
              ) : null}
              <Button variant="outline" asChild>
                <Link href="/">Continue shopping</Link>
              </Button>
            </div>
          </>
        )}
      </div>
    </Container>
  );
}
