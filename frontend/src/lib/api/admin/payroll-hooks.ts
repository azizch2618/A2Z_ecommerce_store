"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createAdminLiveQueryOptions } from "./admin-query-options";
import {
  approvePayrollPeriod,
  calculatePayrollPeriod,
  fetchEmployeePayrollHistory,
  fetchPayrollDashboard,
  fetchPayrollPeriods,
  fetchPayslips,
  postPayrollPeriod,
} from "./payroll-service";

export const payrollQueryKeys = {
  all: ["payroll"] as const,
  dashboard: () => [...payrollQueryKeys.all, "dashboard"] as const,
  periods: (params?: object) => [...payrollQueryKeys.all, "periods", params ?? {}] as const,
  payslips: (params?: object) => [...payrollQueryKeys.all, "payslips", params ?? {}] as const,
  employeeHistory: (id: string) => [...payrollQueryKeys.all, "employee-history", id] as const,
};

export function usePayrollDashboard() {
  return useQuery(
    createAdminLiveQueryOptions(
      "payroll-dashboard",
      payrollQueryKeys.dashboard(),
      fetchPayrollDashboard
    )
  );
}

export function usePayrollPeriods(params?: { status?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "payroll-periods",
      payrollQueryKeys.periods(params),
      () => fetchPayrollPeriods(params)
    )
  );
}

export function usePayslips(params?: { periodId?: string; employeeId?: string }) {
  return useQuery(
    createAdminLiveQueryOptions(
      "payroll-payslips",
      payrollQueryKeys.payslips(params),
      () => fetchPayslips(params)
    )
  );
}

export function useEmployeePayrollHistory(employeeId: string) {
  return useQuery({
    ...createAdminLiveQueryOptions(
      "payroll-employee-history",
      payrollQueryKeys.employeeHistory(employeeId),
      () => fetchEmployeePayrollHistory(employeeId)
    ),
    enabled: Boolean(employeeId),
  });
}

export function useCalculatePayrollPeriod() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: calculatePayrollPeriod,
    onSuccess: () => void qc.invalidateQueries({ queryKey: payrollQueryKeys.all }),
  });
}

export function useApprovePayrollPeriod() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      approvePayrollPeriod(id, comment),
    onSuccess: () => void qc.invalidateQueries({ queryKey: payrollQueryKeys.all }),
  });
}

export function usePostPayrollPeriod() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: postPayrollPeriod,
    onSuccess: () => void qc.invalidateQueries({ queryKey: payrollQueryKeys.all }),
  });
}
