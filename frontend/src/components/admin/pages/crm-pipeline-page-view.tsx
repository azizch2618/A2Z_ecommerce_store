"use client";

import Link from "next/link";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { CrmKanbanBoard } from "@/components/admin/crm/crm-kanban-board";
import { Button } from "@/components/ui/button";
import { useCrmPipeline } from "@/lib/api/admin/crm-hooks";

function CrmPipelinePageView() {
  const { data, isLoading, isError } = useCrmPipeline();

  return (
    <AdminListPage
      title="Pipeline"
      description="Drag leads between stages — New through Won/Lost."
      isLoading={isLoading}
      isError={isError}
      actions={
        <Button variant="outline" asChild>
          <Link href="/admin-dashboard/crm">CRM dashboard</Link>
        </Button>
      }
    >
      <AdminCard title="Kanban board">
        {data ? <CrmKanbanBoard columns={data} /> : null}
      </AdminCard>
    </AdminListPage>
  );
}

export { CrmPipelinePageView };
