export interface HrmDashboardKpis {
  headcount: number;
  onLeaveToday: number;
  clockedInToday: number;
  pendingLeaveRequests: number;
  activeAssetAssignments: number;
  annualLeaveRemainingDays: number;
}

export interface Employee {
  id: string;
  employeeNumber: string;
  firstName: string;
  lastName: string;
  fullName: string;
  email: string;
  phone: string;
  jobTitle: string;
  employmentType: string;
  hireDate: string;
  status: string;
  dateOfBirth: string | null;
  emergencyContact: Record<string, unknown>;
  departmentId: string | null;
  departmentName: string | null;
  costCenterId: string | null;
  costCenterName: string | null;
  managerId: string | null;
  managerName: string | null;
  userId: string | null;
  leaveBalances?: LeaveBalance[];
  documents?: EmployeeDocument[];
}

export interface LeaveBalance {
  leaveType: string;
  balanceDays: number;
  usedDays: number;
  remainingDays: number;
}

export interface EmployeeDocument {
  id: string;
  documentType: string;
  title: string;
  fileUrl: string | null;
  originalFilename: string;
  expiryDate: string | null;
  notes: string;
  uploadedBy: { id: string; email: string } | null;
  createdAt: string;
}

export interface LeaveRequest {
  id: string;
  requestNumber: string;
  employeeId: string;
  employeeName: string;
  leaveType: string;
  startDate: string;
  endDate: string;
  days: number;
  reason: string;
  status: string;
  submittedBy: { id: string; email: string } | null;
  approvedBy: { id: string; email: string } | null;
  createdAt: string;
}

export interface HrmAsset {
  id: string;
  assetNumber: string;
  name: string;
  category: string;
  serialNumber: string;
  status: string;
  notes: string;
}

export interface AssetAssignment {
  id: string;
  assetId: string;
  assetNumber: string;
  assetName: string;
  employeeId: string;
  employeeName: string;
  status: string;
  issuedAt: string;
  returnedAt: string | null;
  conditionOnIssue: string;
  conditionOnReturn: string;
}

export interface OrgStructureEmployee {
  id: string;
  employeeNumber: string;
  fullName: string;
  jobTitle: string;
  managerId: string | null;
  status: string;
}

export interface OrgStructureDepartment {
  id: string;
  code: string;
  name: string;
  businessUnit: string;
  employees: OrgStructureEmployee[];
  headcount: number;
}

export interface OrgStructure {
  companyId: string;
  companyName: string;
  departments: OrgStructureDepartment[];
  totalHeadcount: number;
}
