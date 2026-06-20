import { apiGet, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  CreateOrderPayload,
  OrderDetail,
  OrderListParams,
  OrderListResponse,
} from "../types/order";

/** Place order from cart (checkout) */
export async function createOrder(
  payload: CreateOrderPayload
): Promise<OrderDetail> {
  return apiPost<OrderDetail, CreateOrderPayload>(
    API_ENDPOINTS.orders.create,
    payload
  );
}

/** Customer order history */
export async function fetchOrders(
  params?: OrderListParams
): Promise<OrderListResponse> {
  return apiGet<OrderListResponse>(API_ENDPOINTS.orders.list, { params });
}

/** Single order detail */
export async function fetchOrderById(orderId: string): Promise<OrderDetail> {
  return apiGet<OrderDetail>(API_ENDPOINTS.orders.byId(orderId));
}

/** Cancel a pending order */
export async function cancelOrder(orderId: string): Promise<OrderDetail> {
  return apiPost<OrderDetail>(API_ENDPOINTS.orders.cancel(orderId));
}

/** Reorder — add previous order items to cart */
export async function reorder(orderId: string): Promise<{ cart_id: string }> {
  return apiPost<{ cart_id: string }>(API_ENDPOINTS.orders.reorder(orderId));
}
