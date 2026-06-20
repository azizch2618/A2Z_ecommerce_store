import type { ApiAddress, ListQueryParams, PaginatedResponse } from "./common";

export type TradeTier = "bronze" | "silver" | "gold" | "platinum";

export type QuoteStatus =
  | "draft"
  | "pending_approval"
  | "approved"
  | "rejected"
  | "sent"
  | "accepted"
  | "expired"
  | "converted"
  | "declined";

export interface TradeAccount {
  id: string;
  account_number: string;
  tier: TradeTier;
  status: "approved" | "pending" | "suspended" | "rejected";
  credit_limit_cents: number;
  credit_used_cents: number;
  credit_available_cents: number;
  payment_terms_days: number;
  organization: {
    id: string;
    legal_name: string;
    trading_name: string | null;
    abn: string;
    abn_verified: boolean;
  };
}

export interface TradeAccountApplyPayload {
  legal_name: string;
  trading_name?: string;
  abn: string;
  acn?: string;
  business_email: string;
  business_phone: string;
  business_address: ApiAddress;
  customer_segment: "trade" | "contractor" | "business";
  estimated_monthly_spend?: string;
  notes?: string;
}

export interface TradeAccountApplyResponse {
  organization: { id: string };
  trade_account_status: string;
  message: string;
}

export interface QuoteLine {
  id: string;
  variant_id: string;
  sku: string;
  product_name: string;
  quantity: number;
  unit_price_ex_gst_cents: number;
  line_total_inc_gst_cents: number;
}

export interface Quote {
  id: string;
  quote_number: string;
  status: QuoteStatus;
  valid_until: string;
  total_inc_gst_cents: number;
  currency_code: "AUD";
  lines: QuoteLine[];
  created_at: string;
}

export type QuoteListParams = ListQueryParams & {
  status?: QuoteStatus;
};

export type QuoteListResponse = PaginatedResponse<Quote>;
