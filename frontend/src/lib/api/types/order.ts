import type { ApiAddress, ListQueryParams, PaginatedResponse } from "./common";

export type OrderStatus =
  | "pending"
  | "awaiting_payment"
  | "paid"
  | "packed"
  | "shipped"
  | "delivered"
  | "cancelled"
  | "refunded";

export type PaymentStatus =
  | "pending"
  | "authorized"
  | "paid"
  | "failed"
  | "refunded";

export type PaymentMethod =
  | "card"
  | "paypal"
  | "bank_transfer"
  | "trade_credit";

export interface OrderLineItem {
  id: string;
  sku: string;
  product_name: string;
  variant_name: string | null;
  quantity: number;
  unit_price_ex_gst_cents: number;
  unit_gst_cents: number;
  gst_rate: number;
  line_total_inc_gst_cents: number;
}

export interface OrderTotals {
  subtotal_ex_gst_cents: number;
  gst_total_cents: number;
  shipping_ex_gst_cents: number;
  shipping_gst_cents: number;
  discount_cents: number;
  total_inc_gst_cents: number;
  currency_code: "AUD";
}

export interface OrderSummary {
  id: string;
  order_number: string;
  status: OrderStatus;
  payment_status: PaymentStatus;
  item_count: number;
  total_inc_gst_cents: number;
  currency_code: "AUD";
  placed_at: string;
}

export interface OrderDetail extends OrderSummary {
  items: OrderLineItem[];
  totals: OrderTotals;
  billing_address: ApiAddress;
  shipping_address: ApiAddress;
  shipping_method: {
    id: string;
    name: string;
    carrier: string | null;
  };
  payment: {
    id: string;
    status: PaymentStatus;
    client_secret?: string | null;
  } | null;
}

export interface CreateOrderPayload {
  cart_id: string;
  email?: string;
  billing_address: ApiAddress;
  shipping_address?: ApiAddress;
  shipping_method_id: string;
  warehouse_id?: string;
  payment_method: PaymentMethod;
  po_number?: string;
  customer_notes?: string;
  guest_checkout?: boolean;
}

export interface OrderListParams extends ListQueryParams {
  status?: OrderStatus;
}

export type OrderListResponse = PaginatedResponse<OrderSummary>;
