"use client";

import type { ReactNode } from "react";
import { useState } from "react";

import { AdminSidebar } from "@/components/admin/layout/admin-sidebar";
import { AdminTopbar } from "@/components/admin/layout/admin-topbar";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

export interface AdminShellProps {
  children: ReactNode;
  className?: string;
}

function AdminShell({ children, className }: AdminShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      <div className="flex min-h-screen">
        <AdminSidebar className="fixed inset-y-0 left-0 z-40 hidden w-[260px] lg:flex" />

        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetContent side="left" className="w-[280px] p-0">
            <AdminSidebar onNavigate={() => setMobileOpen(false)} className="w-full border-0" />
          </SheetContent>
        </Sheet>

        <div className="flex min-w-0 flex-1 flex-col lg:pl-[260px]">
          <AdminTopbar onMenuClick={() => setMobileOpen(true)} />
          <main className={cn("flex-1 p-4 md:p-6 lg:p-8", className)}>{children}</main>
        </div>
      </div>
    </div>
  );
}

export { AdminShell };
