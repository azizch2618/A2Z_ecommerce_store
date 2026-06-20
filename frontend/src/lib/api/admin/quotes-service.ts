import { apiGet, apiPatch, apiPost } from "../client";
import { API_BASE_URL, API_ENDPOINTS } from "../config";
import type { Quote, QuoteDashboardKpis } from "./quotes-types";

function unwrapList<T>(payload: { data?: T[] } | T[]): T[] {
  if (Array.isArray(payload)) return payload;
  return payload.data ?? [];
}

export async function fetchQuotesDashboard(): Promise<QuoteDashboardKpis> {
  return apiGet<QuoteDashboardKpis>(API_ENDPOINTS.quotes.dashboard);
}

export async function fetchQuotes(params?: {
  status?: string;
  search?: string;
}): Promise<Quote[]> {
  const rows = await apiGet<{ data: Quote[] }>(API_ENDPOINTS.quotes.list, { params });
  return unwrapList(rows);
}

export async function fetchQuoteDetail(id: string): Promise<Quote> {
  return apiGet<Quote>(API_ENDPOINTS.quotes.detail(id));
}

export async function createQuote(payload: {
  customerId?: string;
  partyId?: string;
  tradeAccountId?: string;
  opportunityId?: string;
  notes?: string;
  termsAndConditions?: string;
  validUntil?: string;
}): Promise<Quote> {
  return apiPost<Quote>(API_ENDPOINTS.quotes.list, payload);
}

export async function updateQuote(
  id: string,
  payload: Partial<{
    notes: string;
    termsAndConditions: string;
    validUntil: string;
    discountCents: number;
  }>
): Promise<Quote> {
  return apiPatch<Quote>(API_ENDPOINTS.quotes.detail(id), payload);
}

export async function addQuoteLine(
  quoteId: string,
  payload: {
    variantId: string;
    quantity: number;
    unitPriceExGstCents?: number;
    discountCents?: number;
  }
): Promise<Quote> {
  return apiPost<Quote>(API_ENDPOINTS.quotes.lines(quoteId), payload);
}

export async function submitQuote(id: string): Promise<Quote> {
  return apiPost<Quote>(API_ENDPOINTS.quotes.submit(id), {});
}

export async function approveQuote(id: string, comment?: string): Promise<Quote> {
  return apiPost<Quote>(API_ENDPOINTS.quotes.approve(id), { comment: comment ?? "" });
}

export async function rejectQuote(id: string, comment?: string): Promise<Quote> {
  return apiPost<Quote>(API_ENDPOINTS.quotes.reject(id), { comment: comment ?? "" });
}

export async function sendQuote(id: string): Promise<Quote> {
  return apiPost<Quote>(API_ENDPOINTS.quotes.send(id), {});
}

export async function convertQuote(id: string): Promise<{
  orderId: string;
  orderNumber: string;
  quote: Quote;
}> {
  return apiPost(API_ENDPOINTS.quotes.convert(id), {});
}

export function quotePdfUrl(id: string): string {
  return `${API_BASE_URL}${API_ENDPOINTS.quotes.pdf(id)}`;
}

export async function acceptCustomerQuote(id: string): Promise<Quote> {
  return apiPost<Quote>(API_ENDPOINTS.quotes.customerAccept(id), {});
}

export async function rejectCustomerQuote(id: string, reason?: string): Promise<Quote> {
  return apiPost<Quote>(API_ENDPOINTS.quotes.customerReject(id), { reason: reason ?? "" });
}

export async function fetchCustomerQuotes(): Promise<Quote[]> {
  const rows = await apiGet<{ data: Quote[] }>(API_ENDPOINTS.quotes.customerList);
  return unwrapList(rows);
}

export async function fetchCustomerQuoteDetail(id: string): Promise<Quote> {
  return apiGet<Quote>(API_ENDPOINTS.quotes.customerDetail(id));
}
