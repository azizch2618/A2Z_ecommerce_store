import { apiGet } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  AdminCustomerDetail,
  AdminCustomerOrderSummary,
  CrmTimelineEntry,
} from "./types";
import type { Quote } from "./quotes-types";

function mapTimelineEntry(row: Record<string, unknown>): CrmTimelineEntry {
  return {
    id: String(row.id),
    entryType: (row.entryType ?? row.entry_type ?? "activity") as CrmTimelineEntry["entryType"],
    activityType: (row.activityType ?? row.activity_type) as CrmTimelineEntry["activityType"],
    title: String(row.title ?? ""),
    body: String(row.body ?? ""),
    occurredAt: String(row.occurredAt ?? row.occurred_at ?? ""),
    actorEmail: (row.actorEmail ?? row.actor_email ?? null) as string | null,
  };
}

function mapOrder(row: Record<string, unknown>): AdminCustomerOrderSummary {
  return {
    id: String(row.id),
    orderNumber: String(row.order_number ?? row.orderNumber ?? ""),
    status: String(row.status ?? ""),
    paymentStatus: String(row.payment_status ?? row.paymentStatus ?? ""),
    itemCount: Number(row.item_count ?? row.itemCount ?? 0),
    totalIncGstCents: Number(row.total_inc_gst_cents ?? row.totalIncGstCents ?? 0),
    currencyCode: String(row.currency_code ?? row.currencyCode ?? "AUD"),
    placedAt: (row.placed_at ?? row.placedAt ?? null) as string | null,
    customerName: String(row.customer_name ?? row.customerName ?? ""),
    customerEmail: String(row.customer_email ?? row.customerEmail ?? ""),
  };
}

export async function fetchAdminCustomerDetail(id: string): Promise<AdminCustomerDetail> {
  const response = await apiGet<Record<string, unknown>>(API_ENDPOINTS.admin.customer(id));
  return {
    profile: response.profile as AdminCustomerDetail["profile"],
    partyId: (response.partyId as string | null) ?? null,
    lifetimeValue: response.lifetimeValue as AdminCustomerDetail["lifetimeValue"],
    tradeAccount: (response.tradeAccount as AdminCustomerDetail["tradeAccount"]) ?? null,
    orders: ((response.orders as Record<string, unknown>[]) ?? []).map(mapOrder),
    quotes: (response.quotes as Quote[]) ?? [],
    crmActivities: ((response.crmActivities as Record<string, unknown>[]) ?? []).map(
      mapTimelineEntry
    ),
  };
}
