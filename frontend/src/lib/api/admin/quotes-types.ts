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

export interface QuoteLine {
  id: string;
  variantId: string;
  sku: string;
  productName: string;
  quantity: number;
  unitPriceExGstCents: number;
  discountCents: number;
  lineGstCents: number;
  lineSubtotalExGstCents: number;
  lineTotalIncGstCents: number;
}

export interface Quote {
  id: string;
  quoteNumber: string;
  status: QuoteStatus;
  validUntil: string | null;
  subtotalExGstCents: number;
  gstTotalCents: number;
  discountCents: number;
  totalIncGstCents: number;
  currencyCode: string;
  notes: string;
  termsAndConditions: string;
  partyId: string | null;
  partyName: string | null;
  customerId: string | null;
  tradeAccountId: string | null;
  opportunityId: string | null;
  createdBy: { id: string; email: string } | null;
  sentAt: string | null;
  acceptedAt: string | null;
  convertedOrderId: string | null;
  convertedOrderNumber: string | null;
  createdAt: string;
  updatedAt: string;
  lines: QuoteLine[];
}

export interface QuoteDashboardKpis {
  draftQuotes: number;
  pendingApproval: number;
  accepted: number;
  converted: number;
  conversionRate: number;
}
