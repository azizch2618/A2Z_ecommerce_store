import { Suspense } from "react";

import CheckoutFailurePage from "./checkout-failure-client";

export const metadata = {
  title: "Payment failed | A2Z Tools",
  description: "Your payment could not be processed.",
};

export default function Page() {
  return (
    <Suspense fallback={null}>
      <CheckoutFailurePage />
    </Suspense>
  );
}
