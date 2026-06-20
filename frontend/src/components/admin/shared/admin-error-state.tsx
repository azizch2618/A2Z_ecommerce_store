"use client";

import { AlertCircle } from "lucide-react";

export interface AdminErrorStateProps {
  title?: string;
  message?: string;
}

function AdminErrorState({
  title = "Failed to load data",
  message = "The admin API could not be reached. Check that you are signed in and the backend is running.",
}: AdminErrorStateProps) {
  return (
    <div
      role="alert"
      className="flex min-h-[40vh] flex-col items-center justify-center gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-8 text-center"
    >
      <AlertCircle className="size-10 text-destructive" aria-hidden />
      <h2 className="text-lg font-semibold text-foreground">{title}</h2>
      <p className="max-w-md text-sm text-muted-foreground">{message}</p>
    </div>
  );
}

export { AdminErrorState };
