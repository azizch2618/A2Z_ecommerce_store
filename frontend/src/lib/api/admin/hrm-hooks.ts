"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createAdminLiveQueryOptions } from "./admin-query-options";
import {
  approveLeaveRequest,
  fetchAssetAssignments,
  fetchEmployeeDetail,
  fetchEmployees,
  fetchHrmDashboard,
  fetchLeaveRequests,
  fetchOrgStructure,
  rejectLeaveRequest,
  submitLeaveRequest,
} from "./hrm-service";

export const hrmQueryKeys = {
  all: ["hrm"] as const,
  dashboard: () => [...hrmQueryKeys.all, "dashboard"] as const,
  orgStructure: () => [...hrmQueryKeys.all, "org-structure"] as const,
  employees: (params?: object) => [...hrmQueryKeys.all, "employees", params ?? {}] as const,
  employee: (id: string) => [...hrmQueryKeys.all, "employee", id] as const,
  leaveRequests: (params?: object) =>
    [...hrmQueryKeys.all, "leave-requests", params ?? {}] as const,
  assetAssignments: () => [...hrmQueryKeys.all, "asset-assignments"] as const,
};

export function useHrmDashboard() {
  return useQuery(
    createAdminLiveQueryOptions("hrm-dashboard", hrmQueryKeys.dashboard(), fetchHrmDashboard)
  );
}

export function useOrgStructure() {
  return useQuery(
    createAdminLiveQueryOptions(
      "hrm-org-structure",
      hrmQueryKeys.orgStructure(),
      fetchOrgStructure
    )
  );
}

export function useEmployees(params?: { status?: string; search?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "hrm-employees",
      hrmQueryKeys.employees(params),
      () => fetchEmployees(params)
    )
  );
}

export function useEmployeeDetail(id: string) {
  return useQuery({
    ...createAdminLiveQueryOptions(
      "hrm-employee-detail",
      hrmQueryKeys.employee(id),
      () => fetchEmployeeDetail(id)
    ),
    enabled: Boolean(id),
  });
}

export function useLeaveRequests(params?: { status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "hrm-leave-requests",
      hrmQueryKeys.leaveRequests(params),
      () => fetchLeaveRequests(params)
    )
  );
}

export function useAssetAssignments() {
  return useQuery(
    createAdminLiveQueryOptions(
      "hrm-asset-assignments",
      hrmQueryKeys.assetAssignments(),
      fetchAssetAssignments
    )
  );
}

export function useSubmitLeaveRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: submitLeaveRequest,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: hrmQueryKeys.all });
    },
  });
}

export function useApproveLeaveRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      approveLeaveRequest(id, comment),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: hrmQueryKeys.all });
    },
  });
}

export function useRejectLeaveRequest() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      rejectLeaveRequest(id, comment),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: hrmQueryKeys.all });
    },
  });
}
