"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createAdminLiveQueryOptions } from "./admin-query-options";
import {
  assignPutawayBin,
  completeWmsPick,
  fetchBinInventory,
  fetchCycleCounts,
  fetchPutawayTaskDetail,
  fetchPutawayTasks,
  fetchWmsBins,
  fetchWmsDashboard,
  fetchWmsPickDetail,
  fetchWmsPicks,
  fetchWmsTransfers,
  recordCycleCount,
  recordWmsPick,
  startWmsPick,
} from "./wms-service";

export const wmsQueryKeys = {
  all: ["wms"] as const,
  dashboard: () => [...wmsQueryKeys.all, "dashboard"] as const,
  bins: (params?: object) => [...wmsQueryKeys.all, "bins", params ?? {}] as const,
  binInventory: (params?: object) =>
    [...wmsQueryKeys.all, "bin-inventory", params ?? {}] as const,
  transfers: (params?: object) => [...wmsQueryKeys.all, "transfers", params ?? {}] as const,
  picks: (params?: object) => [...wmsQueryKeys.all, "picks", params ?? {}] as const,
  pick: (id: string) => [...wmsQueryKeys.all, "pick", id] as const,
  putaway: (params?: object) => [...wmsQueryKeys.all, "putaway", params ?? {}] as const,
  putawayTask: (id: string) => [...wmsQueryKeys.all, "putaway-task", id] as const,
  cycleCounts: (params?: object) =>
    [...wmsQueryKeys.all, "cycle-counts", params ?? {}] as const,
};

export function useWmsDashboard() {
  return useQuery(
    createAdminLiveQueryOptions("wms-dashboard", wmsQueryKeys.dashboard(), fetchWmsDashboard)
  );
}

export function useWmsBins(params?: { warehouseCode?: string }) {
  return useQuery(
    createAdminLiveQueryOptions("wms-bins", wmsQueryKeys.bins(params), () => fetchWmsBins(params))
  );
}

export function useBinInventory(params?: { warehouseCode?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "wms-bin-inventory",
      wmsQueryKeys.binInventory(params),
      () => fetchBinInventory(params)
    )
  );
}

export function useWmsTransfers(params?: { status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "wms-transfers",
      wmsQueryKeys.transfers(params),
      () => fetchWmsTransfers(params)
    )
  );
}

export function useWmsPicks(params?: { status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions("wms-picks", wmsQueryKeys.picks(params), () => fetchWmsPicks(params))
  );
}

export function useWmsPickDetail(id: string) {
  return useQuery({
    ...createAdminLiveQueryOptions("wms-pick-detail", wmsQueryKeys.pick(id), () =>
      fetchWmsPickDetail(id)
    ),
    enabled: Boolean(id),
  });
}

export function useStartWmsPick() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: startWmsPick,
    onSuccess: (_d, id) => {
      void qc.invalidateQueries({ queryKey: wmsQueryKeys.pick(id) });
      void qc.invalidateQueries({ queryKey: wmsQueryKeys.all });
    },
  });
}

export function useRecordWmsPick() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      ...payload
    }: {
      id: string;
      lineId: string;
      quantity: number;
      fromBinId?: string;
    }) => recordWmsPick(id, payload),
    onSuccess: (_d, vars) => {
      void qc.invalidateQueries({ queryKey: wmsQueryKeys.pick(vars.id) });
      void qc.invalidateQueries({ queryKey: wmsQueryKeys.all });
    },
  });
}

export function useCompleteWmsPick() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: completeWmsPick,
    onSuccess: (_d, id) => {
      void qc.invalidateQueries({ queryKey: wmsQueryKeys.pick(id) });
      void qc.invalidateQueries({ queryKey: wmsQueryKeys.all });
    },
  });
}

export function usePutawayTasks(params?: { status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "wms-putaway",
      wmsQueryKeys.putaway(params),
      () => fetchPutawayTasks(params)
    )
  );
}

export function usePutawayTaskDetail(id: string) {
  return useQuery({
    ...createAdminLiveQueryOptions(
      "wms-putaway-detail",
      wmsQueryKeys.putawayTask(id),
      () => fetchPutawayTaskDetail(id)
    ),
    enabled: Boolean(id),
  });
}

export function useAssignPutawayBin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      taskId,
      ...payload
    }: {
      taskId: string;
      lineId: string;
      targetBinId: string;
      quantity: number;
    }) => assignPutawayBin(taskId, payload),
    onSuccess: (_d, vars) => {
      void qc.invalidateQueries({ queryKey: wmsQueryKeys.putawayTask(vars.taskId) });
      void qc.invalidateQueries({ queryKey: wmsQueryKeys.all });
    },
  });
}

export function useCycleCounts(params?: { status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "wms-cycle-counts",
      wmsQueryKeys.cycleCounts(params),
      () => fetchCycleCounts(params)
    )
  );
}

export function useRecordCycleCount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      countId,
      ...payload
    }: {
      countId: string;
      lineId: string;
      countedQty: number;
    }) => recordCycleCount(countId, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: wmsQueryKeys.all });
    },
  });
}
