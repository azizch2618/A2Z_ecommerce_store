import type { CheckoutFormState } from "@/types/checkout";

export const checkoutBreadcrumbs = [
  { label: "Home", href: "/" },
  { label: "Cart", href: "/cart" },
  { label: "Checkout" },
];

export const shippingMethods = [
  {
    id: "standard",
    label: "Standard Delivery",
    description: "Australia Post · 5–7 business days",
    estimatedDelivery: "5–7 business days",
    getPriceIncGst: (subtotalIncGst: number) =>
      subtotalIncGst >= 150 ? 0 : 14.95,
  },
  {
    id: "express",
    label: "Express Delivery",
    description: "Australia Post Express · 2–3 business days",
    estimatedDelivery: "2–3 business days",
    getPriceIncGst: () => 24.95,
  },
  {
    id: "click-collect",
    label: "Click & Collect",
    description: "Pick up from Sydney warehouse · Ready in 24 hrs",
    estimatedDelivery: "Usually within 24 hours",
    getPriceIncGst: () => 0,
  },
] as const;

export const paymentMethods = [
  {
    id: "card",
    label: "Credit Card",
    description: "Visa, Mastercard, American Express",
  },
  {
    id: "paypal",
    label: "PayPal",
    description: "Pay securely with your PayPal account",
  },
  {
    id: "bank_transfer",
    label: "Bank Transfer",
    description: "Direct deposit — order held until payment clears",
  },
] as const;

export const defaultCheckoutForm: CheckoutFormState = {
  customer: {
    firstName: "",
    lastName: "",
    company: "",
    email: "",
    phone: "",
  },
  shipping: {
    line1: "",
    line2: "",
    city: "",
    state: "",
    postcode: "",
    country: "Australia",
  },
  shippingMethodId: "standard",
  paymentMethodId: "card",
  cardName: "",
  cardNumber: "",
  cardExpiry: "",
  cardCvc: "",
};

export function getShippingPriceIncGst(
  methodId: string,
  subtotalIncGst: number
): number {
  const method = shippingMethods.find((item) => item.id === methodId);
  return method ? method.getPriceIncGst(subtotalIncGst) : 14.95;
}

export function getEstimatedDelivery(methodId: string): string {
  const method = shippingMethods.find((item) => item.id === methodId);
  return method?.estimatedDelivery ?? "5–7 business days";
}

export function getShippingMethodLabel(methodId: string): string {
  const method = shippingMethods.find((item) => item.id === methodId);
  return method?.label ?? "Standard Delivery";
}
