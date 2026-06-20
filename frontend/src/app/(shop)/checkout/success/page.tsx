import { Suspense } from "react";

import CheckoutSuccessPage from "./checkout-success-client";

export const metadata = {
  title: "Payment successful | A2Z Tools",
  description: "Your payment has been received.",
};

export default function Page() {
  return (
    <Suspense fallback={null}>
      <CheckoutSuccessPage />
    </Suspense>
  );
}
