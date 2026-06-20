import { apiGet, apiPatch, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  InventoryLevel,
  InventoryListParams,
  InventoryListResponse,
  InventoryNotification,
  LedgerSummary,
  LowStockAlert,
  MovementListParams,
  NotificationListResponse,
  ReorderLevelPayload,
  StockAdjustmentPayload,
  StockInPayload,
  StockMovement,
  StockMovementListResponse,
  StockOutPayload,
  StockTransferPayload,
  TransferListResponse,
  ValuationSummary,
} from "../types/inventory";

export async function fetchInventoryLevels(
  params?: InventoryListParams
): Promise<InventoryListResponse> {
  return apiGet<InventoryListResponse>(API_ENDPOINTS.inventory.levels, { params });
}

export async function updateReorderLevels(
  levelId: string,
  payload: ReorderLevelPayload
): Promise<InventoryLevel> {
  return apiPatch<InventoryLevel, ReorderLevelPayload>(
    API_ENDPOINTS.inventory.level(levelId),
    payload
  );
}

export async function fetchStockMovements(
  params?: MovementListParams
): Promise<StockMovementListResponse> {
  return apiGet<StockMovementListResponse>(API_ENDPOINTS.inventory.movements, {
    params,
  });
}

export async function fetchTransfers(params?: {
  warehouse_code?: string;
  sku?: string;
  cursor?: string;
}): Promise<TransferListResponse> {
  return apiGet<TransferListResponse>(API_ENDPOINTS.inventory.transfers, {
    params,
  });
}

export async function fetchValuationSummary(params?: {
  warehouse_code?: string;
  limit?: number;
}): Promise<ValuationSummary> {
  return apiGet<ValuationSummary>(API_ENDPOINTS.inventory.valuation, { params });
}

export async function fetchLedgerSummary(params?: {
  warehouse_code?: string;
  date_from?: string;
  date_to?: string;
}): Promise<LedgerSummary> {
  return apiGet<LedgerSummary>(API_ENDPOINTS.inventory.ledgerSummary, {
    params,
  });
}

export async function fetchLowStockAlerts(): Promise<{ data: LowStockAlert[] }> {
  return apiGet<{ data: LowStockAlert[] }>(API_ENDPOINTS.inventory.lowStockAlerts);
}

export async function fetchInventoryNotifications(params?: {
  status?: string;
}): Promise<NotificationListResponse> {
  return apiGet<NotificationListResponse>(API_ENDPOINTS.inventory.notifications, {
    params,
  });
}

export async function fetchNotificationUnreadCount(): Promise<{ count: number }> {
  return apiGet<{ count: number }>(API_ENDPOINTS.inventory.notificationCount);
}

export async function acknowledgeNotification(
  alertId: string
): Promise<InventoryNotification> {
  return apiPost<InventoryNotification>(
    API_ENDPOINTS.inventory.acknowledgeNotification(alertId)
  );
}

export async function stockIn(
  payload: StockInPayload
): Promise<{ movement: StockMovement; inventory: InventoryLevel }> {
  return apiPost(API_ENDPOINTS.inventory.stockIn, payload);
}

export async function stockOut(
  payload: StockOutPayload
): Promise<{ movement: StockMovement; inventory: InventoryLevel }> {
  return apiPost(API_ENDPOINTS.inventory.stockOut, payload);
}

export async function stockAdjustment(
  payload: StockAdjustmentPayload
): Promise<{ movement: StockMovement; inventory: InventoryLevel }> {
  return apiPost(API_ENDPOINTS.inventory.adjustments, payload);
}

export async function stockTransfer(
  payload: StockTransferPayload
): Promise<{ movement: StockMovement; inventory: InventoryLevel }> {
  return apiPost(API_ENDPOINTS.inventory.stockTransfer, payload);
}
