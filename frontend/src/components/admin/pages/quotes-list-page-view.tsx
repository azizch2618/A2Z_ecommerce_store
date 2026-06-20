"use client";

import Link from "next/link";
import { useState } from "react";

import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { QuotesTable } from "@/components/admin/quotes/quotes-table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useQuotes } from "@/lib/api/admin/quotes-hooks";

function QuotesListPageView() {
  const [status, setStatus] = useState<string>("all");
  const [search, setSearch] = useState("");
  const quotes = useQuotes({
    status: status === "all" ? undefined : status,
    search: search || undefined,
  });

  return (
    <AdminListPage
      title="All quotes"
      description="Search and filter quotations across the sales pipeline."
      isLoading={quotes.isLoading}
      isError={quotes.isError}
      actions={
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/quotes">Dashboard</Link>
        </Button>
      }
    >
      <div className="mb-4 flex flex-wrap gap-3">
        <Input
          placeholder="Search quote # or customer…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <Select value={status} onValueChange={setStatus}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="pending_approval">Pending approval</SelectItem>
            <SelectItem value="approved">Approved</SelectItem>
            <SelectItem value="sent">Sent</SelectItem>
            <SelectItem value="accepted">Accepted</SelectItem>
            <SelectItem value="converted">Converted</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <QuotesTable quotes={quotes.data ?? []} />
    </AdminListPage>
  );
}

export { QuotesListPageView };
