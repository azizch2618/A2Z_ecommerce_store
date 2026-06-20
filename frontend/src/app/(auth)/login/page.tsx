import { Suspense } from "react";

import { AuthLayout, LoginForm } from "@/components/auth";
import { Spinner } from "@/components/ui/spinner";

export const metadata = {
  title: "Sign in | A2Z Tools",
  description: "Sign in to your A2Z Tools account to manage orders, trade pricing, and quotes.",
};

function LoginFormFallback() {
  return (
    <div className="flex min-h-[200px] items-center justify-center">
      <Spinner className="size-6" />
    </div>
  );
}

export default function LoginPage() {
  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to manage orders, trade pricing, and saved quotes."
    >
      <Suspense fallback={<LoginFormFallback />}>
        <LoginForm />
      </Suspense>
    </AuthLayout>
  );
}
