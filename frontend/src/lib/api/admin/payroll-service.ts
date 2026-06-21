import { apiGet, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  EmployeePayrollHistory,
  PayrollDashboardKpis,
  PayrollPeriod,
  Payslip,
  SalaryStructure,
} from "./payroll-types";

function unwrapList<T>(payload: { data?: T[] } | T[]): T[] {
  if (Array.isArray(payload)) return payload;
  return payload.data ?? [];
}

export async function fetchPayrollDashboard(): Promise<PayrollDashboardKpis> {
  return apiGet<PayrollDashboardKpis>(API_ENDPOINTS.payroll.dashboard);
}

export async function fetchPayrollPeriods(params?: { status?: string }): Promise<PayrollPeriod[]> {
  const rows = await apiGet<{ data: PayrollPeriod[] }>(API_ENDPOINTS.payroll.periods, { params });
  return unwrapList(rows);
}

export async function fetchPayrollPeriodDetail(id: string): Promise<PayrollPeriod> {
  return apiGet<PayrollPeriod>(API_ENDPOINTS.payroll.period(id));
}

export async function createPayrollPeriod(payload: {
  name: string;
  periodStart: string;
  periodEnd: string;
  payDate: string;
  notes?: string;
}): Promise<PayrollPeriod> {
  return apiPost<PayrollPeriod>(API_ENDPOINTS.payroll.periods, payload);
}

export async function calculatePayrollPeriod(id: string): Promise<PayrollPeriod> {
  return apiPost<PayrollPeriod>(API_ENDPOINTS.payroll.periodCalculate(id), {});
}

export async function approvePayrollPeriod(id: string, comment?: string): Promise<PayrollPeriod> {
  return apiPost<PayrollPeriod>(API_ENDPOINTS.payroll.periodApprove(id), { comment: comment ?? "" });
}

export async function postPayrollPeriod(id: string): Promise<PayrollPeriod> {
  return apiPost<PayrollPeriod>(API_ENDPOINTS.payroll.periodPost(id), {});
}

export async function fetchPayslips(params?: {
  periodId?: string;
  employeeId?: string;
}): Promise<Payslip[]> {
  const rows = await apiGet<{ data: Payslip[] }>(API_ENDPOINTS.payroll.payslips, { params });
  return unwrapList(rows);
}

export async function fetchEmployeePayrollHistory(employeeId: string): Promise<EmployeePayrollHistory> {
  return apiGet<EmployeePayrollHistory>(API_ENDPOINTS.payroll.employeeHistory(employeeId));
}

export async function fetchSalaryStructures(employeeId: string): Promise<SalaryStructure[]> {
  const rows = await apiGet<{ data: SalaryStructure[] }>(API_ENDPOINTS.payroll.salaryStructures, {
    params: { employeeId },
  });
  return unwrapList(rows);
}

export function payslipPdfUrl(payslipId: string): string {
  return API_ENDPOINTS.payroll.payslipPdf(payslipId);
}
