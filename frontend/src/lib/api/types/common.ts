/** Shared API types aligned with docs/API_SPECIFICATION.md */

export type AustralianState =
  | "NSW"
  | "VIC"
  | "QLD"
  | "SA"
  | "WA"
  | "TAS"
  | "NT"
  | "ACT";

export type StockStatus =
  | "in_stock"
  | "low_stock"
  | "backorder"
  | "out_of_stock";

export type CurrencyCode = "AUD";

export interface ApiTimestamps {
  created_at: string;
  updated_at: string;
}

export interface ApiPagination {
  next_cursor: string | null;
  has_more: boolean;
  limit: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: ApiPagination;
}

export interface PriceBlock {
  amount_ex_gst_cents: number;
  gst_cents: number;
  amount_inc_gst_cents: number;
  gst_rate: number;
  currency_code: CurrencyCode;
  compare_at_cents: number | null;
  is_trade_price: boolean;
}

export interface StockBlock {
  status: StockStatus;
  quantity_available: number;
  lead_time_days: number | null;
}

export interface ApiAddress {
  id?: string;
  label?: string | null;
  line1: string;
  line2?: string | null;
  suburb: string;
  state: AustralianState;
  postcode: string;
  country?: string;
  is_default_billing?: boolean;
  is_default_shipping?: boolean;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: Record<string, string[]> | Array<Record<string, string>>;
  };
}

export interface ListQueryParams {
  cursor?: string | null;
  limit?: number;
}

export interface BrandRef {
  id: string;
  name: string;
  slug: string;
  logo_url?: string | null;
}

export interface ImageRef {
  url: string;
  alt_text?: string | null;
}
