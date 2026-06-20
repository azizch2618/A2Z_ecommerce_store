"use client";

import * as React from "react";
import { Elements, PaymentElement, useElements, useStripe } from "@stripe/react-stripe-js";
import { loadStripe, type StripeElementsOptions } from "@stripe/stripe-js";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";

interface StripePaymentFormProps {
  publishableKey: string;
  clientSecret: string;
  orderId: string;
  isSubmitting?: boolean;
}

function StripeConfirmButton({
  orderId,
  isParentSubmitting,
}: {
  orderId: string;
  isParentSubmitting?: boolean;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const router = useRouter();
  const [isPaying, setIsPaying] = React.useState(false);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);

  const handlePay = async () => {
    if (!stripe || !elements) return;

    setIsPaying(true);
    setErrorMessage(null);

    const returnUrl = `${window.location.origin}/checkout/success?order_id=${orderId}`;

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: { return_url: returnUrl },
      redirect: "if_required",
    });

    if (error) {
      setErrorMessage(error.message ?? "Payment failed. Please try again.");
      setIsPaying(false);
      router.push(`/checkout/failure?order_id=${orderId}`);
      return;
    }

    router.push(`/checkout/success?order_id=${orderId}`);
  };

  const busy = isPaying || isParentSubmitting;

  return (
    <div className="space-y-4">
      <PaymentElement
        options={{
          layout: "tabs",
        }}
      />
      {errorMessage ? (
        <p className="text-sm text-destructive" role="alert">
          {errorMessage}
        </p>
      ) : null}
      <Button
        type="button"
        className="w-full"
        size="lg"
        onClick={() => void handlePay()}
        disabled={!stripe || !elements || busy}
      >
        {busy ? (
          <>
            <Loader2 className="mr-2 size-4 animate-spin" />
            Processing payment…
          </>
        ) : (
          "Pay securely"
        )}
      </Button>
    </div>
  );
}

export function StripePaymentForm({
  publishableKey,
  clientSecret,
  orderId,
  isSubmitting,
}: StripePaymentFormProps) {
  const stripePromise = React.useMemo(
    () => loadStripe(publishableKey),
    [publishableKey]
  );

  const options = React.useMemo<StripeElementsOptions>(
    () => ({
      clientSecret,
      appearance: {
        theme: "stripe",
        variables: {
          colorPrimary: "#1e40af",
        },
      },
    }),
    [clientSecret]
  );

  return (
    <Elements stripe={stripePromise} options={options}>
      <StripeConfirmButton orderId={orderId} isParentSubmitting={isSubmitting} />
    </Elements>
  );
}
