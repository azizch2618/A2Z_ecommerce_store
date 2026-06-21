"use client";

import { AdminCard } from "@/components/admin/shared/admin-card";
import type { OrgStructure } from "@/lib/api/admin/hrm-types";

export interface OrgStructureTreeProps {
  org: OrgStructure;
}

function OrgStructureTree({ org }: OrgStructureTreeProps) {
  return (
    <div className="space-y-4">
      <AdminCard title={org.companyName}>
        <p className="text-sm text-muted-foreground">
          Total headcount: <span className="font-medium text-foreground">{org.totalHeadcount}</span>
        </p>
      </AdminCard>

      <div className="grid gap-4 md:grid-cols-2">
        {org.departments.map((dept) => (
          <AdminCard key={dept.id} title={`${dept.name} (${dept.code})`}>
            <p className="mb-3 text-xs text-muted-foreground">{dept.businessUnit}</p>
            {dept.employees.length === 0 ? (
              <p className="text-sm text-muted-foreground">No active employees.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {dept.employees.map((emp) => (
                  <li key={emp.id} className="flex flex-col gap-0.5 border-b pb-2 last:border-0">
                    <span className="font-medium">{emp.fullName}</span>
                    <span className="text-muted-foreground">
                      {emp.jobTitle} · {emp.employeeNumber}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </AdminCard>
        ))}
      </div>
    </div>
  );
}

export { OrgStructureTree };
