import { apiGet } from "../client";
import { API_ENDPOINTS } from "../config";
import { hasAuthTokens } from "../auth/token-storage";
import type {
  AdminCustomer,
  AdminDashboardData,
  AdminOrder,
  AdminProduct,
  AdminSupplier,
  LowStockItem,
  OutOfStockItem,
  RevenueDataPoint,
  RevenuePeriod,
  TradeApplication,
} from "./types";
import { withAdminApiLog } from "./log-admin-api-error";

type RawDashboardPayload = Omit<
  AdminDashboardData,
  "lowStock" | "outOfStock" | "recentCustomers" | "tradeApplications" | "suppliers"
> & {
  lowStock?: LowStockItem[];
  outOfStock?: OutOfStockItem[];
  lowStockItems?: LowStockItem[];
  outOfStockItems?: OutOfStockItem[];
  recentCustomers?: AdminCustomer[];
  tradeApplications?: TradeApplication[];
  suppliers?: AdminSupplier[];
};

function requireAuth(): void {
  if (!hasAuthTokens()) {
    throw new Error("Admin authentication required");
  }
}

function normalizeDashboardPayload(raw: RawDashboardPayload): AdminDashboardData {
  return {
    ...raw,
    lowStock: raw.lowStock ?? raw.lowStockItems ?? [],
    outOfStock: raw.outOfStock ?? raw.outOfStockItems ?? [],
    recentCustomers: raw.recentCustomers ?? [],
    tradeApplications: raw.tradeApplications ?? [],
    suppliers: raw.suppliers ?? [],
    notifications: raw.notifications ?? [],
  };
}

export async function fetchAdminDashboard(): Promise<AdminDashboardData> {
  requireAuth();
  const raw = await apiGet<RawDashboardPayload>(API_ENDPOINTS.admin.dashboard);
  return normalizeDashboardPayload(raw);
}

export async function fetchAdminOrders(): Promise<AdminOrder[]> {
  requireAuth();
  const response = await apiGet<{
    data: Array<{
      id: string;
      order_number: string;
      customer_name: string;
      customer_email: string;
      total_inc_gst_cents: number;
      status: string;
      placed_at: string;
    }>;
  }>(API_ENDPOINTS.orders.list);
  return response.data.map((order) => ({
    id: order.id,
    orderNumber: order.order_number,
    customerName: order.customer_name,
    customerEmail: order.customer_email,
    amountCents: order.total_inc_gst_cents,
    status: order.status as AdminOrder["status"],
    placedAt: order.placed_at,
  }));
}

export async function fetchAdminCustomers(): Promise<AdminCustomer[]> {
  requireAuth();
  const response = await apiGet<{ data: AdminCustomer[] }>(
    API_ENDPOINTS.admin.customers
  );
  return response.data;
}

export async function fetchAdminProducts(): Promise<AdminProduct[]> {
  const { fetchAdminProductsList } = await import("./operational-service");
  return fetchAdminProductsList();
}

export async function fetchAdminTradeApplications(): Promise<TradeApplication[]> {
  const dashboard = await fetchAdminDashboard();
  return dashboard.tradeApplications;
}

export async function fetchAdminSuppliers(): Promise<AdminSupplier[]> {
  const dashboard = await fetchAdminDashboard();
  return dashboard.suppliers;
}

export async function fetchRevenueByPeriod(
  period: RevenuePeriod
): Promise<RevenueDataPoint[]> {
  const dashboard = await withAdminApiLog("revenue", fetchAdminDashboard);
  return dashboard.revenue[period];
}
