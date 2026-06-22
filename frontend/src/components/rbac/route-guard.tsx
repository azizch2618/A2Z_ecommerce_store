"use client";

import type { ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { hasAuthTokens } from "@/lib/api/auth/token-storage";
import { useAuth } from "@/lib/api/hooks/use-auth";
import { authDebug } from "@/lib/auth/auth-debug";

export interface RouteGuardProps {
  children: ReactNode;
  /** Redirect target when unauthenticated */
  redirectTo?: string;
  /** Require email verification */
  requireVerified?: boolean;
}

/**
 * Protects storefront account routes — requires authentication.
 */
function RouteGuard({
  children,
  redirectTo = "/login",
  requireVerified = false,
}: RouteGuardProps) {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    if (isLoading) return;

    const hasSession = hasAuthTokens();
    if (!hasSession || !isAuthenticated) {
      authDebug("route-guard", "redirecting to login", {
        pathname: window.location.pathname,
        hasSession,
        isAuthenticated,
        isLoading,
      });
      const params = new URLSearchParams({ redirect: window.location.pathname });
      router.replace(`${redirectTo}?${params}`);
      return;
    }

    authDebug("route-guard", "access granted", {
      pathname: window.location.pathname,
      email: user?.email,
    });
  }, [isAuthenticated, isLoading, redirectTo, router, user?.email]);

  if (isLoading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="size-8 animate-spin rounded-full border-2 border-brand-navy border-t-transparent" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (requireVerified && user && !user.email_verified) {
    return (
      <div className="mx-auto max-w-lg p-8 text-center">
        <h2 className="text-lg font-semibold">Verify your email</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Please verify your email address to access this page.
        </p>
      </div>
    );
  }

  return children;
}

export { RouteGuard };
