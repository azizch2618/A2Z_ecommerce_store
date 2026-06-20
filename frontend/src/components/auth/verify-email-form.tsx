"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

import { useVerifyEmail } from "@/lib/api/hooks/use-auth";
import { isApiError } from "@/lib/api/errors";
import { AuthCard } from "@/components/auth/auth-card";
import { Button } from "@/components/ui/button";

type VerifyState = "idle" | "verifying" | "success" | "error";

function VerifyEmailForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const verifyMutation = useVerifyEmail();
  const [state, setState] = React.useState<VerifyState>("idle");
  const [message, setMessage] = React.useState<string>("");

  const uid = searchParams.get("uid") ?? "";
  const token = searchParams.get("token") ?? "";

  React.useEffect(() => {
    if (!uid || !token) {
      setState("error");
      setMessage("This verification link is invalid or incomplete.");
      return;
    }

    let cancelled = false;

    async function activateAccount() {
      setState("verifying");
      try {
        const response = await verifyMutation.mutateAsync({ uid, token });
        if (cancelled) return;
        setState("success");
        setMessage(response.message);
      } catch (error) {
        if (cancelled) return;
        setState("error");
        setMessage(
          isApiError(error)
            ? error.message
            : "Could not verify your email. The link may have expired."
        );
      }
    }

    void activateAccount();

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- run once for link params
  }, [uid, token]);

  return (
    <AuthCard>
      <div className="space-y-5 text-center">
        {state === "verifying" ? (
          <>
            <Loader2 className="mx-auto size-10 animate-spin text-brand-blue" aria-hidden />
            <div>
              <h2 className="text-xl font-semibold text-foreground">Verifying your email</h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Please wait while we activate your account…
              </p>
            </div>
          </>
        ) : null}

        {state === "success" ? (
          <>
            <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-brand-blue-light/40 dark:bg-brand-blue-light/10">
              <CheckCircle2 className="size-7 text-brand-blue" aria-hidden />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-foreground">Email verified</h2>
              <p className="mt-2 text-sm text-muted-foreground">{message}</p>
            </div>
            <Button className="w-full" onClick={() => router.push("/account")}>
              Go to my account
            </Button>
          </>
        ) : null}

        {state === "error" ? (
          <>
            <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-destructive/10">
              <AlertCircle className="size-7 text-destructive" aria-hidden />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-foreground">Verification failed</h2>
              <p className="mt-2 text-sm text-muted-foreground">{message}</p>
            </div>
            <div className="flex flex-col gap-2">
              <Button asChild variant="outline" className="w-full">
                <Link href="/login">Sign in</Link>
              </Button>
              <Button asChild className="w-full">
                <Link href="/register">Create a new account</Link>
              </Button>
            </div>
          </>
        ) : null}
      </div>
    </AuthCard>
  );
}

export { VerifyEmailForm };
