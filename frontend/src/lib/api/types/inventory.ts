import type { PaginatedResponse, PriceBlock } from "./common";

export type StockMovementType =
  | "receipt"
  | "sale"
  | "return"
  | "adjustment"
  | "transfer_in"
  | "transfer_out"
  | "reservation"
  | "release";

export type InventoryAlertType = "low_stock" | "out_of_stock";
export type InventoryAlertStatus = "active" | "acknowledged" | "resolved";

export interface InventoryLevel {
  id: string;
  sku: string;
  variant_id: string;
  product_name: string;
  warehouse_code: string;
  warehouse_name: string;
  quantity_on_hand: number;
  quantity_reserved: number;
  quantity_available: number;
  cost_price_cents: number;
  sale_price_cents: number;
  reorder_point: number;
  reorder_quantity: number;
  valuation_ex_gst_cents: number;
  valuation: PriceBlock;
  currency_code: string;
  updated_at: string;
}

export interface StockMovement {
  id: string;
  movement_number: string;
  sku: string;
  variant_id: string;
  warehouse_code: string;
  transaction_type: StockMovementType;
  quantity: number;
  quantity_change: number;
  quantity_after: number;
  cost_price_cents: number | null;
  value_ex_gst_cents: number | null;
  valuation: PriceBlock | null;
  currency_code: string;
  transfer_group_id: string | null;
  reference_type: string;
  reference_id: number | null;
  notes: string;
  created_by_email: string | null;
  created_at: string;
}

export interface TransferGroup {
  transfer_group_id: string;
  sku: string;
  product_name: string;
  from_warehouse_code: string;
  to_warehouse_code: string | null;
  quantity: number;
  notes: string;
  created_at: string;
  created_by_email: string | null;
}

export interface LowStockAlert extends InventoryLevel {
  alert_level: InventoryAlertType | "ok";
  shortfall: number;
}

export interface InventoryNotification {
  id: string;
  sku: string;
  product_name: string;
  warehouse_code: string;
  inventory_level_id: string;
  alert_type: InventoryAlertType;
  status: InventoryAlertStatus;
  quantity_on_hand: number;
  reorder_point: number;
  shortfall: number;
  message: string;
  acknowledged_at: string | null;
  created_at: string;
}

export interface WarehouseValuation extends PriceBlock {
  warehouse_code: string;
  warehouse_name: string;
  sku_count: number;
  total_units: number;
}

export interface ValuationSummary extends PriceBlock {
  as_at: string | null;
  warehouse_code: string | null;
  sku_count: number;
  total_units: number;
  low_stock_value: PriceBlock;
  by_warehouse: WarehouseValuation[];
  valuation_method: string;
  tax_note: string;
  top_skus_by_value: Array<
    {
      sku: string;
      product_name: string;
      warehouse_code: string;
      quantity_on_hand: number;
      average_cost_cents: number;
    } & PriceBlock
  >;
}

export interface LedgerPeriodSummary extends PriceBlock {
  count: number;
  quantity: number;
}

export interface LedgerSummary {
  period: { from: string | null; to: string | null };
  warehouse_code: string | null;
  currency_code: string;
  gst_rate: number;
  total_movements: number;
  receipts: LedgerPeriodSummary;
  issues: LedgerPeriodSummary;
  transfers: { count: number };
  by_type: (LedgerPeriodSummary & { transaction_type: string; label: string })[];
  tax_note: string;
}

export interface StockInPayload {
  sku: string;
  warehouse_code: string;
  quantity: number;
  cost_price_cents: number;
  notes?: string;
}

export interface StockOutPayload {
  sku: string;
  warehouse_code: string;
  quantity: number;
  notes?: string;
}

export interface StockAdjustmentPayload {
  sku: string;
  warehouse_code: string;
  quantity_change: number;
  cost_price_cents?: number;
  notes?: string;
}

export interface StockTransferPayload {
  sku: string;
  from_warehouse_code: string;
  to_warehouse_code: string;
  quantity: number;
  notes?: string;
}

export interface ReorderLevelPayload {
  reorder_point: number;
  reorder_quantity: number;
}

export type InventoryListResponse = PaginatedResponse<InventoryLevel>;
export type StockMovementListResponse = PaginatedResponse<StockMovement>;
export type TransferListResponse = PaginatedResponse<TransferGroup>;
export type NotificationListResponse = PaginatedResponse<InventoryNotification>;

export interface InventoryListParams {
  warehouse_code?: string;
  sku?: string;
  low_stock?: boolean;
  cursor?: string;
  limit?: number;
}

export interface MovementListParams {
  warehouse_code?: string;
  sku?: string;
  transaction_type?: StockMovementType;
  date_from?: string;
  date_to?: string;
  cursor?: string;
  limit?: number;
}
