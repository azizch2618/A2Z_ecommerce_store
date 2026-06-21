export interface PayrollDashboardKpis {
  totalPayrollYtdCents: number;
  totalGrossYtdCents: number;
  postedRunsCount: number;
  pendingApprovalCount: number;
  departmentCosts: Array<{
    departmentName: string;
    totalCents: number;
    headcount: number;
  }>;
  upcomingRuns: Array<{
    id: string;
    periodNumber: string;
    name: string;
    payDate: string;
    status: string;
  }>;
}

export interface PayrollPeriod {
  id: string;
  periodNumber: string;
  name: string;
  periodStart: string;
  periodEnd: string;
  payDate: string;
  status: string;
  totalGrossCents: number;
  totalNetCents: number;
  totalDeductionsCents: number;
  totalSuperCents: number;
  totalPaygCents: number;
  notes?: string;
}

export interface SalaryComponent {
  id: string;
  componentType: string;
  code: string;
  name: string;
  amountCents: number;
  isTaxable: boolean;
  isSuperable: boolean;
}

export interface SalaryStructure {
  id: string;
  employeeId: string;
  employeeName: string;
  effectiveFrom: string;
  effectiveTo: string | null;
  payFrequency: string;
  awardCode: string;
  isActive: boolean;
  components: SalaryComponent[];
}

export interface PayslipLine {
  id: string;
  lineType: string;
  code: string;
  description: string;
  amountCents: number;
}

export interface Payslip {
  id: string;
  payslipNumber: string;
  payrollPeriodId: string;
  periodName: string;
  periodNumber: string;
  employeeId: string;
  employeeName: string;
  employeeNumber: string;
  departmentName: string | null;
  status: string;
  grossCents: number;
  netCents: number;
  totalAllowancesCents: number;
  totalDeductionsCents: number;
  leaveDeductionCents: number;
  overtimeCents: number;
  paygWithholdingCents: number;
  superCents: number;
  payDate: string;
  lines: PayslipLine[];
}

export interface EmployeePayrollHistory {
  employeeId: string;
  employeeName: string;
  payslips: Payslip[];
  salaryStructures: SalaryStructure[];
}
