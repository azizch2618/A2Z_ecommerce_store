import { fetchOrderById } from "../services/orders.service";
import { API_BASE_URL, API_ENDPOINTS } from "../config";
import type { OrderDetail } from "../types/order";
import { hasAuthTokens } from "../auth/token-storage";

export async function fetchAdminOrderDetail(orderId: string): Promise<OrderDetail> {
  if (!hasAuthTokens()) {
    throw new Error("Admin authentication required");
  }
  return fetchOrderById(orderId);
}

export function orderInvoiceUrl(orderId: string): string {
  return `${API_BASE_URL}${API_ENDPOINTS.orders.invoice(orderId)}`;
}
