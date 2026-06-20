"use client";

import Link from "next/link";
import { useState } from "react";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { CrmLeadsTable } from "@/components/admin/crm/crm-leads-table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useCreateCrmLead, useCrmLeads } from "@/lib/api/admin/crm-hooks";

function CrmLeadsPageView() {
  const [search, setSearch] = useState("");
  const { data, isLoading, isError } = useCrmLeads({ search: search || undefined });
  const createLead = useCreateCrmLead();

  const handleCreate = () => {
    void createLead.mutateAsync({
      title: "New inbound lead",
      companyName: "Prospect Co",
      contactName: "Contact",
      source: "website",
    });
  };

  return (
    <AdminListPage
      title="Leads"
      description="Manage sales leads linked to ERP Party records — no duplicate customer master data."
      isLoading={isLoading}
      isError={isError}
      actions={
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link href="/admin-dashboard/crm/pipeline">Pipeline</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/admin-dashboard/crm">CRM dashboard</Link>
          </Button>
          <Button onClick={handleCreate} disabled={createLead.isPending}>
            Add lead
          </Button>
        </div>
      }
    >
      <div className="max-w-sm">
        <Input
          placeholder="Search leads…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <AdminCard title="All leads">
        <CrmLeadsTable leads={data ?? []} />
      </AdminCard>
    </AdminListPage>
  );
}

export { CrmLeadsPageView };
