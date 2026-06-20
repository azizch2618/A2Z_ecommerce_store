"use client";

import type { ReactNode } from "react";
import { AlertCircle, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { isApiError, type ApiError } from "@/lib/api/errors";
import { cn } from "@/lib/utils";

export interface QueryStateProps {
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isEmpty?: boolean;
  emptyMessage?: string;
  loadingMessage?: string;
  children: ReactNode;
  className?: string;
  onRetry?: () => void;
}

function getErrorMessage(error: Error | null): string {
  if (!error) return "Something went wrong.";
  if (isApiError(error)) return error.message;
  return error.message;
}

export function QueryState({
  isLoading,
  isError,
  error,
  isEmpty = false,
  emptyMessage = "No results found.",
  loadingMessage = "Loading…",
  children,
  className,
  onRetry,
}: QueryStateProps) {
  if (isLoading) {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center gap-3 py-16 text-muted-foreground",
          className
        )}
        role="status"
        aria-live="polite"
      >
        <Loader2 className="size-8 animate-spin text-brand-amber" aria-hidden />
        <p className="text-sm">{loadingMessage}</p>
      </div>
    );
  }

  if (isError) {
    const apiError = isApiError(error) ? (error as ApiError) : null;
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center gap-4 rounded-xl border border-destructive/30 bg-destructive/5 px-6 py-12 text-center",
          className
        )}
        role="alert"
      >
        <AlertCircle className="size-10 text-destructive" aria-hidden />
        <div className="space-y-1">
          <p className="font-medium text-foreground">Unable to load data</p>
          <p className="text-sm text-muted-foreground">
            {getErrorMessage(error)}
          </p>
          {apiError?.code ? (
            <p className="font-mono text-xs text-muted-foreground">
              {apiError.code}
            </p>
          ) : null}
        </div>
        {onRetry ? (
          <Button type="button" variant="outline" size="sm" onClick={onRetry}>
            Try again
          </Button>
        ) : null}
      </div>
    );
  }

  if (isEmpty) {
    return (
      <div
        className={cn(
          "flex flex-col items-center justify-center py-16 text-center text-muted-foreground",
          className
        )}
      >
        <p className="text-sm">{emptyMessage}</p>
      </div>
    );
  }

  return <>{children}</>;
}
