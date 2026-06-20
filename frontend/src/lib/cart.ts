const GST_RATE = 0.1;
export const FREE_SHIPPING_THRESHOLD = 150;
export const STANDARD_SHIPPING_INC_GST = 14.95;

export { formatAud } from "@/lib/format/currency";

/** Australian GST is included in displayed prices (1/11 of inc-GST total). */
export function calculateGstFromInclusive(totalIncGst: number) {
  const gstAmount = (totalIncGst / (1 + GST_RATE)) * GST_RATE;
  const exGst = totalIncGst - gstAmount;
  return {
    gstAmount: roundCurrency(gstAmount),
    exGst: roundCurrency(exGst),
  };
}

export function calculateShipping(subtotalIncGst: number): number {
  return subtotalIncGst >= FREE_SHIPPING_THRESHOLD ? 0 : STANDARD_SHIPPING_INC_GST;
}

function roundCurrency(value: number): number {
  return Math.round(value * 100) / 100;
}

export function calculateCartSummary(
  items: Array<{
    priceValue: number;
    tradePriceValue?: number;
    quantity: number;
  }>
) {
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);
  const subtotalIncGst = roundCurrency(
    items.reduce((sum, item) => sum + item.priceValue * item.quantity, 0)
  );
  const tradeSubtotalIncGst = roundCurrency(
    items.reduce(
      (sum, item) =>
        sum + (item.tradePriceValue ?? item.priceValue) * item.quantity,
      0
    )
  );
  const hasTradePricing = items.some(
    (item) =>
      item.tradePriceValue !== undefined &&
      item.tradePriceValue < item.priceValue
  );
  const tradeSavingsIncGst = roundCurrency(subtotalIncGst - tradeSubtotalIncGst);
  const shippingIncGst = calculateShipping(subtotalIncGst);
  const tradeShippingIncGst = calculateShipping(tradeSubtotalIncGst);
  const totalIncGst = roundCurrency(subtotalIncGst + shippingIncGst);
  const tradeTotalIncGst = roundCurrency(tradeSubtotalIncGst + tradeShippingIncGst);
  const gstBreakdown = calculateGstFromInclusive(totalIncGst);
  const tradeGstBreakdown = calculateGstFromInclusive(tradeTotalIncGst);
  const amountUntilFreeShipping = Math.max(
    0,
    roundCurrency(FREE_SHIPPING_THRESHOLD - subtotalIncGst)
  );

  return {
    subtotalIncGst,
    shippingIncGst,
    totalIncGst,
    gstAmount: gstBreakdown.gstAmount,
    subtotalExGst: gstBreakdown.exGst,
    itemCount,
    freeShippingThreshold: FREE_SHIPPING_THRESHOLD,
    amountUntilFreeShipping,
    qualifiesForFreeShipping: subtotalIncGst >= FREE_SHIPPING_THRESHOLD,
    hasTradePricing,
    tradeSubtotalIncGst,
    tradeShippingIncGst,
    tradeTotalIncGst,
    tradeGstAmount: tradeGstBreakdown.gstAmount,
    tradeSubtotalExGst: tradeGstBreakdown.exGst,
    tradeSavingsIncGst,
  };
}

export function calculateCheckoutSummary(
  items: Array<{
    priceValue: number;
    tradePriceValue?: number;
    quantity: number;
  }>,
  shippingIncGst: number
) {
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);
  const retailSubtotalIncGst = roundCurrency(
    items.reduce((sum, item) => sum + item.priceValue * item.quantity, 0)
  );
  const tradeSubtotalIncGst = roundCurrency(
    items.reduce(
      (sum, item) =>
        sum + (item.tradePriceValue ?? item.priceValue) * item.quantity,
      0
    )
  );
  const hasTradePricing = items.some(
    (item) =>
      item.tradePriceValue !== undefined &&
      item.tradePriceValue < item.priceValue
  );
  const tradeDiscountIncGst = roundCurrency(
    retailSubtotalIncGst - tradeSubtotalIncGst
  );
  const subtotalIncGst = tradeSubtotalIncGst;
  const totalIncGst = roundCurrency(subtotalIncGst + shippingIncGst);
  const { gstAmount, exGst } = calculateGstFromInclusive(totalIncGst);

  return {
    retailSubtotalIncGst,
    tradeSubtotalIncGst,
    tradeDiscountIncGst,
    subtotalIncGst,
    shippingIncGst,
    totalIncGst,
    gstAmount,
    subtotalExGst: exGst,
    itemCount,
    hasTradePricing,
  };
}
