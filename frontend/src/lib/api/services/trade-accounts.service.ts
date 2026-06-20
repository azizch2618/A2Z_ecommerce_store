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

/** List B2B quotes / RFQs */
export async function fetchQuotes(
  params?: QuoteListParams
): Promise<QuoteListResponse> {
  return apiGet<QuoteListResponse>(API_ENDPOINTS.tradeAccounts.quotes, {
    params,
  });
}

/** Single quote detail */
export async function fetchQuoteById(quoteId: string): Promise<Quote> {
  return apiGet<Quote>(API_ENDPOINTS.tradeAccounts.quote(quoteId));
}
