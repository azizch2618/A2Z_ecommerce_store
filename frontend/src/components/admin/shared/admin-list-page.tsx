"use client";

import type { ReactNode } from "react";

import { AdminErrorState } from "@/components/admin/shared/admin-error-state";
import { AdminPageHeader } from "@/components/admin/shared/admin-page-header";
import { Spinner } from "@/components/ui/spinner";
import { cn } from "@/lib/utils";

export interface AdminListPageProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  isLoading?: boolean;
  isError?: boolean;
  errorMessage?: string;
  children: ReactNode;
  className?: string;
}

function AdminListPage({
  title,
  description,
  actions,
  isLoading,
  isError,
  errorMessage,
  children,
  className,
}: AdminListPageProps) {
  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Spinner className="size-8" />
      </div>
    );
  }

  if (isError) {
    return <AdminErrorState message={errorMessage} />;
  }

  return (
    <div className={cn("space-y-6", className)}>
      <AdminPageHeader title={title} description={description} actions={actions} />
      {children}
    </div>
  );
}

export { AdminListPage };
