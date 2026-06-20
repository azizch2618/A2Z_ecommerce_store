export interface CartItem {
  id: string;
  productId: string;
  slug: string;
  brand: string;
  name: string;
  sku: string;
  /** Retail unit price inc. GST */
  priceValue: number;
  /** Trade unit price inc. GST (when trade account pricing applies) */
  tradePriceValue?: number;
  quantity: number;
  imageSrc: string;
  imageAlt: string;
  href: string;
  maxQuantity?: number;
}

export interface CartSummary {
  subtotalIncGst: number;
  shippingIncGst: number;
  totalIncGst: number;
  gstAmount: number;
  subtotalExGst: number;
  itemCount: number;
  freeShippingThreshold: number;
  amountUntilFreeShipping: number;
  qualifiesForFreeShipping: boolean;
  /** Trade account pricing */
  hasTradePricing: boolean;
  tradeSubtotalIncGst: number;
  tradeShippingIncGst: number;
  tradeTotalIncGst: number;
  tradeGstAmount: number;
  tradeSubtotalExGst: number;
  tradeSavingsIncGst: number;
}
