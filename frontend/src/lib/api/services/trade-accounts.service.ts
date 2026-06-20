import { apiGet, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  Quote,
  QuoteListParams,
  QuoteListResponse,
  TradeAccount,
  TradeAccountApplyPayload,
  TradeAccountApplyResponse,
} from "../types/trade-account";

/** Current trade account and credit summary */
export async function fetchTradeAccount(): Promise<TradeAccount> {
  return apiGet<TradeAccount>(API_ENDPOINTS.tradeAccounts.me);
}

/** Submit trade account application */
export async function applyForTradeAccount(
  payload: TradeAccountApplyPayload
): Promise<TradeAccountApplyResponse> {
  return apiPost<TradeAccountApplyResponse, TradeAccountApplyPayload>(
    API_ENDPOINTS.tradeAccounts.apply,
    payload
  );
}

/** List B2B quotes / RFQs — uses quotes module customer API */
export async function fetchQuotes(
  params?: QuoteListParams
): Promise<QuoteListResponse> {
  const rows = await apiGet<{ data: Array<Record<string, unknown>> }>(
    API_ENDPOINTS.quotes.customerList,
    { params }
  );
  const data = (rows.data ?? []).map(mapCustomerQuote);
  return {
    data,
    pagination: { next_cursor: null, has_more: false, limit: data.length },
  };
}

/** Single quote detail */
export async function fetchQuoteById(quoteId: string): Promise<Quote> {
  const row = await apiGet<Record<string, unknown>>(API_ENDPOINTS.quotes.customerDetail(quoteId));
  return mapCustomerQuote(row);
}

function mapCustomerQuote(row: Record<string, unknown>): Quote {
  const lines = Array.isArray(row.lines)
    ? (row.lines as Array<Record<string, unknown>>).map((line) => ({
        id: String(line.id),
        variant_id: String(line.variantId),
        sku: String(line.sku),
        product_name: String(line.productName),
        quantity: Number(line.quantity),
        unit_price_ex_gst_cents: Number(line.unitPriceExGstCents),
        line_total_inc_gst_cents: Number(line.lineTotalIncGstCents),
      }))
    : [];

  return {
    id: String(row.id),
    quote_number: String(row.quoteNumber),
    status: row.status as Quote["status"],
    valid_until: String(row.validUntil ?? ""),
    total_inc_gst_cents: Number(row.totalIncGstCents),
    currency_code: "AUD",
    lines,
    created_at: String(row.createdAt),
  };
}
