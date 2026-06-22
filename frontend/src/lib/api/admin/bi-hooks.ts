"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createAdminLiveQueryOptions } from "./admin-query-options";
import {
  createScheduledReport,
  exportBiReport,
  fetchBiSnapshot,
  fetchExecutiveSnapshot,
  fetchFinanceAnalytics,
  fetchHrAnalytics,
  fetchInventoryAnalytics,
  fetchKpiEvaluations,
  fetchProcurementAnalytics,
  fetchSalesAnalytics,
  fetchScheduledReports,
} from "./bi-service";

export const biQueryKeys = {
  all: ["bi"] as const,
  executive: () => [...biQueryKeys.all, "executive"] as const,
  snapshot: () => [...biQueryKeys.all, "snapshot"] as const,
  sales: () => [...biQueryKeys.all, "sales"] as const,
  inventory: () => [...biQueryKeys.all, "inventory"] as const,
  procurement: () => [...biQueryKeys.all, "procurement"] as const,
  finance: () => [...biQueryKeys.all, "finance"] as const,
  hr: () => [...biQueryKeys.all, "hr"] as const,
  kpis: () => [...biQueryKeys.all, "kpis"] as const,
  schedules: () => [...biQueryKeys.all, "schedules"] as const,
};

export function useExecutiveSnapshot() {
  return useQuery(
    createAdminLiveQueryOptions("bi-executive", biQueryKeys.executive(), fetchExecutiveSnapshot)
  );
}

export function useBiSnapshot() {
  return useQuery(
    createAdminLiveQueryOptions("bi-snapshot", biQueryKeys.snapshot(), fetchBiSnapshot)
  );
}

export function useSalesAnalytics() {
  return useQuery(
    createAdminLiveQueryOptions("bi-sales", biQueryKeys.sales(), fetchSalesAnalytics)
  );
}

export function useInventoryAnalytics() {
  return useQuery(
    createAdminLiveQueryOptions("bi-inventory", biQueryKeys.inventory(), fetchInventoryAnalytics)
  );
}

export function useProcurementAnalytics() {
  return useQuery(
    createAdminLiveQueryOptions("bi-procurement", biQueryKeys.procurement(), fetchProcurementAnalytics)
  );
}

export function useFinanceAnalytics() {
  return useQuery(
    createAdminLiveQueryOptions("bi-finance", biQueryKeys.finance(), fetchFinanceAnalytics)
  );
}

export function useHrAnalytics() {
  return useQuery(
    createAdminLiveQueryOptions("bi-hr", biQueryKeys.hr(), fetchHrAnalytics)
  );
}

export function useKpiEvaluations() {
  return useQuery(
    createAdminLiveQueryOptions("bi-kpis", biQueryKeys.kpis(), fetchKpiEvaluations)
  );
}

export function useScheduledReports() {
  return useQuery(
    createAdminLiveQueryOptions("bi-schedules", biQueryKeys.schedules(), fetchScheduledReports)
  );
}

export function useCreateScheduledReport() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createScheduledReport,
    onSuccess: () => void qc.invalidateQueries({ queryKey: biQueryKeys.schedules() }),
  });
}

export function useExportBiReport() {
  return useMutation({ mutationFn: exportBiReport });
}
