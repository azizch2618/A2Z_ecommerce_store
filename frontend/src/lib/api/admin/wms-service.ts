import { apiGet, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  BinInventoryRow,
  CycleCount,
  PickList,
  PutawayTask,
  StockTransfer,
  WarehouseBin,
  WmsDashboardKpis,
} from "./wms-types";

function unwrapList<T>(payload: { data?: T[] } | T[]): T[] {
  if (Array.isArray(payload)) return payload;
  return payload.data ?? [];
}

export async function fetchWmsDashboard(): Promise<WmsDashboardKpis> {
  return apiGet<WmsDashboardKpis>(API_ENDPOINTS.wms.dashboard);
}

export async function fetchWmsBins(params?: {
  warehouseCode?: string;
  search?: string;
}): Promise<WarehouseBin[]> {
  const rows = await apiGet<{ data: WarehouseBin[] }>(API_ENDPOINTS.wms.bins, { params });
  return unwrapList(rows);
}

export async function fetchBinInventory(params?: {
  warehouseCode?: string;
  sku?: string;
}): Promise<BinInventoryRow[]> {
  const rows = await apiGet<{ data: BinInventoryRow[] }>(API_ENDPOINTS.wms.binInventory, {
    params,
  });
  return unwrapList(rows);
}

export async function fetchWmsTransfers(params?: { status?: string }): Promise<StockTransfer[]> {
  const rows = await apiGet<{ data: StockTransfer[] }>(API_ENDPOINTS.wms.transfers, { params });
  return unwrapList(rows);
}

export async function fetchWmsPicks(params?: { status?: string }): Promise<PickList[]> {
  const rows = await apiGet<{ data: PickList[] }>(API_ENDPOINTS.wms.picks, { params });
  return unwrapList(rows);
}

export async function fetchWmsPickDetail(id: string): Promise<PickList> {
  return apiGet<PickList>(API_ENDPOINTS.wms.pick(id));
}

export async function startWmsPick(id: string): Promise<PickList> {
  return apiPost<PickList>(API_ENDPOINTS.wms.pickStart(id), {});
}

export async function recordWmsPick(
  id: string,
  payload: { lineId: string; quantity: number; fromBinId?: string }
): Promise<PickList> {
  return apiPost<PickList>(API_ENDPOINTS.wms.pickRecord(id), payload);
}

export async function completeWmsPick(id: string): Promise<PickList> {
  return apiPost<PickList>(API_ENDPOINTS.wms.pickComplete(id), {});
}

export async function fetchPutawayTasks(params?: { status?: string }): Promise<PutawayTask[]> {
  const rows = await apiGet<{ data: PutawayTask[] }>(API_ENDPOINTS.wms.putaway, { params });
  return unwrapList(rows);
}

export async function fetchPutawayTaskDetail(id: string): Promise<PutawayTask> {
  return apiGet<PutawayTask>(API_ENDPOINTS.wms.putawayDetail(id));
}

export async function assignPutawayBin(
  taskId: string,
  payload: { lineId: string; targetBinId: string; quantity: number }
): Promise<PutawayTask> {
  return apiPost<PutawayTask>(API_ENDPOINTS.wms.putawayAssign(taskId), payload);
}

export async function fetchCycleCounts(params?: { status?: string }): Promise<CycleCount[]> {
  const rows = await apiGet<{ data: CycleCount[] }>(API_ENDPOINTS.wms.cycleCounts, { params });
  return unwrapList(rows);
}

export async function recordCycleCount(
  countId: string,
  payload: { lineId: string; countedQty: number }
): Promise<CycleCount> {
  return apiPost<CycleCount>(API_ENDPOINTS.wms.cycleCountRecord(countId), payload);
}
