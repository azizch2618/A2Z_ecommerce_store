import { apiGet, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  AssetAssignment,
  Employee,
  HrmAsset,
  HrmDashboardKpis,
  LeaveRequest,
  OrgStructure,
} from "./hrm-types";

function unwrapList<T>(payload: { data?: T[] } | T[]): T[] {
  if (Array.isArray(payload)) return payload;
  return payload.data ?? [];
}

export async function fetchHrmDashboard(): Promise<HrmDashboardKpis> {
  return apiGet<HrmDashboardKpis>(API_ENDPOINTS.hrm.dashboard);
}

export async function fetchOrgStructure(): Promise<OrgStructure> {
  return apiGet<OrgStructure>(API_ENDPOINTS.hrm.orgStructure);
}

export async function fetchEmployees(params?: {
  status?: string;
  departmentId?: string;
  search?: string;
}): Promise<Employee[]> {
  const rows = await apiGet<{ data: Employee[] }>(API_ENDPOINTS.hrm.employees, { params });
  return unwrapList(rows);
}

export async function fetchEmployeeDetail(id: string): Promise<Employee> {
  return apiGet<Employee>(API_ENDPOINTS.hrm.employee(id));
}

export async function createEmployee(payload: {
  firstName: string;
  lastName: string;
  email: string;
  jobTitle: string;
  employmentType?: string;
  hireDate: string;
  phone?: string;
  departmentId?: string;
  costCenterId?: string;
  managerId?: string;
}): Promise<Employee> {
  return apiPost<Employee>(API_ENDPOINTS.hrm.employees, payload);
}

export async function fetchLeaveRequests(params?: {
  status?: string;
  employeeId?: string;
}): Promise<LeaveRequest[]> {
  const rows = await apiGet<{ data: LeaveRequest[] }>(API_ENDPOINTS.hrm.leaveRequests, {
    params,
  });
  return unwrapList(rows);
}

export async function submitLeaveRequest(id: string): Promise<LeaveRequest> {
  return apiPost<LeaveRequest>(API_ENDPOINTS.hrm.leaveSubmit(id), {});
}

export async function approveLeaveRequest(id: string, comment?: string): Promise<LeaveRequest> {
  return apiPost<LeaveRequest>(API_ENDPOINTS.hrm.leaveApprove(id), { comment: comment ?? "" });
}

export async function rejectLeaveRequest(id: string, comment?: string): Promise<LeaveRequest> {
  return apiPost<LeaveRequest>(API_ENDPOINTS.hrm.leaveReject(id), { comment: comment ?? "" });
}

export async function fetchAssetAssignments(): Promise<AssetAssignment[]> {
  const rows = await apiGet<{ data: AssetAssignment[] }>(API_ENDPOINTS.hrm.assetAssignments);
  return unwrapList(rows);
}

export async function fetchAssets(params?: {
  status?: string;
  category?: string;
}): Promise<HrmAsset[]> {
  const rows = await apiGet<{ data: HrmAsset[] }>(API_ENDPOINTS.hrm.assets, { params });
  return unwrapList(rows);
}
