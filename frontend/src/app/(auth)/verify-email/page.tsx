import { Suspense } from "react";

import { AuthLayout, VerifyEmailForm } from "@/components/auth";

export const metadata = {
  title: "Verify email | A2Z Tools",
  description: "Activate your A2Z Tools account by verifying your email address.",
};

export default function VerifyEmailPage() {
  return (
    <AuthLayout
      title="Verify your email"
      subtitle="Activate your account to access orders, trade pricing, and saved addresses."
    >
      <Suspense fallback={null}>
        <VerifyEmailForm />
      </Suspense>
    </AuthLayout>
  );
}
