import type { PriceBlock, StockBlock } from "./common";

export interface CartLineTotal {
  amount_ex_gst_cents: number;
  gst_cents: number;
  amount_inc_gst_cents: number;
}

export interface CartItem {
  id: string;
  variant_id: string;
  sku: string;
  product_name: string;
  variant_name: string | null;
  image_url: string | null;
  quantity: number;
  price: PriceBlock;
  line_total: CartLineTotal;
  stock: StockBlock;
}

export interface CartTotals {
  subtotal_ex_gst_cents: number;
  gst_cents: number;
  discount_cents: number;
  total_inc_gst_cents: number;
  currency_code: "AUD";
}

export interface CartCoupon {
  code: string;
  description: string | null;
  discount_cents: number;
}

export interface Cart {
  id: string;
  items: CartItem[];
  item_count: number;
  totals: CartTotals;
  coupon: CartCoupon | null;
  updated_at: string;
}

export interface AddToCartPayload {
  variant_id: string;
  quantity: number;
}

export interface UpdateCartItemPayload {
  quantity: number;
}

export interface ApplyCouponPayload {
  code: string;
}

export interface MergeCartPayload {
  session_key: string;
}
