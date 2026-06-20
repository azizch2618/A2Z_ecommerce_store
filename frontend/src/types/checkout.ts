import type { AustralianState } from "@/lib/australian-address";

export interface CheckoutAddress {
  line1: string;
  line2: string;
  city: string;
  state: AustralianState | "";
  postcode: string;
  country: string;
}

export interface CheckoutCustomer {
  firstName: string;
  lastName: string;
  company: string;
  email: string;
  phone: string;
}

export interface CheckoutFormState {
  customer: CheckoutCustomer;
  shipping: CheckoutAddress;
  shippingMethodId: string;
  paymentMethodId: string;
  cardName: string;
  cardNumber: string;
  cardExpiry: string;
  cardCvc: string;
}

export interface CheckoutFormErrors {
  customer?: Partial<Record<keyof CheckoutCustomer, string>>;
  shipping?: Partial<Record<keyof CheckoutAddress, string>>;
  payment?: {
    cardName?: string;
    cardNumber?: string;
    cardExpiry?: string;
    cardCvc?: string;
  };
}

export interface CheckoutOrderTotals {
  retailSubtotalIncGst: number;
  tradeSubtotalIncGst: number;
  tradeDiscountIncGst: number;
  shippingIncGst: number;
  gstAmount: number;
  subtotalExGst: number;
  totalIncGst: number;
  itemCount: number;
  hasTradePricing: boolean;
}
