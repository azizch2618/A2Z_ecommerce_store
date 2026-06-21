"use client";

import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Employee } from "@/lib/api/admin/hrm-types";

const statusVariant: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
  active: "default",
  on_leave: "outline",
  terminated: "destructive",
  suspended: "secondary",
};

export interface EmployeesTableProps {
  employees: Employee[];
  showLinks?: boolean;
}

function EmployeesTable({ employees, showLinks = true }: EmployeesTableProps) {
  if (employees.length === 0) {
    return <p className="text-sm text-muted-foreground">No employees found.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Employee #</TableHead>
          <TableHead>Name</TableHead>
          <TableHead>Job title</TableHead>
          <TableHead>Department</TableHead>
          <TableHead>Status</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {employees.map((employee) => (
          <TableRow key={employee.id}>
            <TableCell className="font-medium">
              {showLinks ? (
                <Link
                  href={`/admin-dashboard/hrm/employees/${employee.id}`}
                  className="hover:underline"
                >
                  {employee.employeeNumber}
                </Link>
              ) : (
                employee.employeeNumber
              )}
            </TableCell>
            <TableCell>{employee.fullName}</TableCell>
            <TableCell>{employee.jobTitle}</TableCell>
            <TableCell>{employee.departmentName ?? "—"}</TableCell>
            <TableCell>
              <Badge variant={statusVariant[employee.status] ?? "secondary"} className="capitalize">
                {employee.status.replace("_", " ")}
              </Badge>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { EmployeesTable };
