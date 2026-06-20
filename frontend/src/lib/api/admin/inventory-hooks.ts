"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { hasAuthTokens } from "../auth/token-storage";
import {
  acknowledgeNotification,
  fetchInventoryLevels,
  fetchInventoryNotifications,
  fetchLedgerSummary,
  fetchLowStockAlerts,
  fetchNotificationUnreadCount,
  fetchStockMovements,
  fetchTransfers,
  fetchValuationSummary,
  stockAdjustment,
  stockIn,
  stockOut,
  stockTransfer,
  updateReorderLevels,
} from "../services/inventory.service";
import type {
  InventoryListParams,
  MovementListParams,
  ReorderLevelPayload,
  StockAdjustmentPayload,
  StockInPayload,
  StockOutPayload,
  StockTransferPayload,
} from "../types/inventory";
import { adminQueryKeys } from "./hooks";

const enabled = () => hasAuthTokens();

export function useInventoryLevels(params?: InventoryListParams) {
  return useQuery({
    queryKey: [...adminQueryKeys.inventory(), "api", params ?? {}],
    queryFn: () => fetchInventoryLevels(params),
    enabled: enabled(),
    staleTime: 30_000,
  });
}

export function useStockMovementsApi(params?: MovementListParams) {
  return useQuery({
    queryKey: [...adminQueryKeys.stockMovements(), "api", params ?? {}],
    queryFn: () => fetchStockMovements(params),
    enabled: enabled(),
  });
}

export function useTransfersApi(params?: { warehouse_code?: string; sku?: string }) {
  return useQuery({
    queryKey: [...adminQueryKeys.all, "transfers", "api", params ?? {}],
    queryFn: () => fetchTransfers(params),
    enabled: enabled(),
  });
}

export function useValuationSummary(params?: { warehouse_code?: string }) {
  return useQuery({
    queryKey: [...adminQueryKeys.all, "valuation", params ?? {}],
    queryFn: () => fetchValuationSummary(params),
    enabled: enabled(),
    staleTime: 60_000,
  });
}

export function useLedgerSummary(params?: {
  warehouse_code?: string;
  date_from?: string;
  date_to?: string;
}) {
  return useQuery({
    queryKey: [...adminQueryKeys.all, "ledger", params ?? {}],
    queryFn: () => fetchLedgerSummary(params),
    enabled: enabled(),
  });
}

export function useLowStockAlertsApi() {
  return useQuery({
    queryKey: [...adminQueryKeys.lowStockAlerts(), "api"],
    queryFn: fetchLowStockAlerts,
    enabled: enabled(),
  });
}

export function useInventoryNotifications(status = "active") {
  return useQuery({
    queryKey: [...adminQueryKeys.all, "notifications", status],
    queryFn: () => fetchInventoryNotifications({ status }),
    enabled: enabled(),
    refetchInterval: 60_000,
  });
}

export function useNotificationUnreadCount() {
  return useQuery({
    queryKey: [...adminQueryKeys.all, "notification-count"],
    queryFn: fetchNotificationUnreadCount,
    enabled: enabled(),
    refetchInterval: 30_000,
  });
}

function useInvalidateInventoryApi() {
  const queryClient = useQueryClient();
  return () => {
    void queryClient.invalidateQueries({ queryKey: adminQueryKeys.inventory() });
    void queryClient.invalidateQueries({ queryKey: adminQueryKeys.stockMovements() });
    void queryClient.invalidateQueries({ queryKey: adminQueryKeys.lowStockAlerts() });
    void queryClient.invalidateQueries({ queryKey: adminQueryKeys.all });
  };
}

export function useStockInApi() {
  const invalidate = useInvalidateInventoryApi();
  return useMutation({
    mutationFn: (payload: StockInPayload) => stockIn(payload),
    onSuccess: invalidate,
  });
}

export function useStockOutApi() {
  const invalidate = useInvalidateInventoryApi();
  return useMutation({
    mutationFn: (payload: StockOutPayload) => stockOut(payload),
    onSuccess: invalidate,
  });
}

export function useStockAdjustmentApi() {
  const invalidate = useInvalidateInventoryApi();
  return useMutation({
    mutationFn: (payload: StockAdjustmentPayload) => stockAdjustment(payload),
    onSuccess: invalidate,
  });
}

export function useStockTransferApi() {
  const invalidate = useInvalidateInventoryApi();
  return useMutation({
    mutationFn: (payload: StockTransferPayload) => stockTransfer(payload),
    onSuccess: invalidate,
  });
}

export function useUpdateReorderLevels() {
  const invalidate = useInvalidateInventoryApi();
  return useMutation({
    mutationFn: ({
      levelId,
      payload,
    }: {
      levelId: string;
      payload: ReorderLevelPayload;
    }) => updateReorderLevels(levelId, payload),
    onSuccess: invalidate,
  });
}

export function useAcknowledgeNotification() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (alertId: string) => acknowledgeNotification(alertId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: adminQueryKeys.all });
    },
  });
}
