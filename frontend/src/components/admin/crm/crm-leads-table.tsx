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
import type { CrmLead } from "@/lib/api/admin/types";

const statusVariant: Record<string, "default" | "secondary" | "success" | "warning" | "destructive"> =
  {
    new: "secondary",
    contacted: "default",
    qualified: "default",
    proposal_sent: "warning",
    won: "success",
    lost: "destructive",
  };

export interface CrmLeadsTableProps {
  leads: CrmLead[];
}

function CrmLeadsTable({ leads }: CrmLeadsTableProps) {
  if (leads.length === 0) {
    return <p className="text-sm text-muted-foreground">No leads yet.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Lead</TableHead>
          <TableHead>Company</TableHead>
          <TableHead>Contact</TableHead>
          <TableHead>Source</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Assigned</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {leads.map((lead) => (
          <TableRow key={lead.id}>
            <TableCell className="font-medium">
              <Link href={`/admin-dashboard/crm/leads/${lead.id}`} className="hover:underline">
                {lead.title}
              </Link>
            </TableCell>
            <TableCell>{lead.companyName || "—"}</TableCell>
            <TableCell>
              <div className="text-sm">{lead.contactName || "—"}</div>
              <div className="text-xs text-muted-foreground">{lead.contactEmail}</div>
            </TableCell>
            <TableCell className="capitalize">{lead.source.replace("_", " ")}</TableCell>
            <TableCell>
              <Badge variant={statusVariant[lead.status] ?? "secondary"} className="capitalize">
                {lead.status.replace("_", " ")}
              </Badge>
            </TableCell>
            <TableCell>{lead.assignedTo?.name ?? "—"}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export { CrmLeadsTable };
