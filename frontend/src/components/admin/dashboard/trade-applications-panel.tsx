"use client";

import { useState } from "react";
import { Check, Eye, X } from "lucide-react";
import { toast } from "sonner";

import type { TradeApplication } from "@/lib/api/admin/types";
import { useUpdateTradeApplication } from "@/lib/api/admin/hooks";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

function formatDate(iso: string) {
  return new Intl.DateTimeFormat("en-AU", { dateStyle: "medium" }).format(new Date(iso));
}

export interface TradeApplicationsPanelProps {
  applications: TradeApplication[];
}

function TradeApplicationsPanel({ applications }: TradeApplicationsPanelProps) {
  const updateTrade = useUpdateTradeApplication();
  const [creditLimit, setCreditLimit] = useState<Record<string, string>>({});

  const pending = applications.filter((a) => a.status === "pending");
  const approved = applications.filter((a) => a.status === "approved");
  const rejected = applications.filter((a) => a.status === "rejected");

  const handleAction = (
    id: string,
    status: "approved" | "rejected",
    creditLimitAud?: string
  ) => {
    const payload: {
      id: string;
      status: "approved" | "rejected";
      credit_limit_cents?: number;
    } = { id, status };

    if (status === "approved" && creditLimitAud) {
      const cents = Math.round(parseFloat(creditLimitAud) * 100);
      if (!Number.isFinite(cents) || cents <= 0) {
        toast.error("Enter a valid credit limit in AUD");
        return;
      }
      payload.credit_limit_cents = cents;
    }

    updateTrade.mutate(payload, {
      onSuccess: () => toast.success(`Application ${status}`),
      onError: () => toast.error("Failed to update application"),
    });
  };

  return (
    <div className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg border border-border bg-muted/30 p-4">
          <p className="text-sm text-muted-foreground">Pending</p>
          <p className="text-2xl font-bold text-warning">{pending.length}</p>
        </div>
        <div className="rounded-lg border border-border bg-muted/30 p-4">
          <p className="text-sm text-muted-foreground">Approved</p>
          <p className="text-2xl font-bold text-success">{approved.length}</p>
        </div>
        <div className="rounded-lg border border-border bg-muted/30 p-4">
          <p className="text-sm text-muted-foreground">Rejected</p>
          <p className="text-2xl font-bold text-error">{rejected.length}</p>
        </div>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Company</TableHead>
            <TableHead>Contact</TableHead>
            <TableHead>ABN</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Submitted</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {applications.map((app) => (
            <TableRow key={app.id}>
              <TableCell className="font-medium">{app.companyName}</TableCell>
              <TableCell>
                <p>{app.contactName}</p>
                <p className="text-xs text-muted-foreground">{app.email}</p>
              </TableCell>
              <TableCell className="font-mono text-xs">{app.abn}</TableCell>
              <TableCell>
                <Badge
                  variant={
                    app.status === "approved"
                      ? "success"
                      : app.status === "pending"
                        ? "warning"
                        : "destructive"
                  }
                  className="capitalize"
                >
                  {app.status}
                </Badge>
              </TableCell>
              <TableCell className="text-sm text-muted-foreground">
                {formatDate(app.submittedAt)}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-2">
                  <Button variant="ghost" size="icon" className="size-8" aria-label="View details">
                    <Eye className="size-4" />
                  </Button>
                  {app.status === "pending" ? (
                    <>
                      <Input
                        type="number"
                        min="0"
                        step="100"
                        placeholder="Credit limit AUD"
                        className="h-8 w-32"
                        value={creditLimit[app.id] ?? "5000"}
                        onChange={(e) =>
                          setCreditLimit((prev) => ({ ...prev, [app.id]: e.target.value }))
                        }
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        className="size-8 text-success"
                        aria-label="Approve"
                        onClick={() =>
                          handleAction(app.id, "approved", creditLimit[app.id] ?? "5000")
                        }
                      >
                        <Check className="size-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="size-8 text-error"
                        aria-label="Reject"
                        onClick={() => handleAction(app.id, "rejected")}
                      >
                        <X className="size-4" />
                      </Button>
                    </>
                  ) : null}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

export { TradeApplicationsPanel };
