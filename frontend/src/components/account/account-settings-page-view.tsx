"use client";

import * as React from "react";
import { Loader2 } from "lucide-react";
import { toast } from "sonner";

import { getAccountBreadcrumbs } from "@/config/account";
import { useAuth, useCurrentUser, useUpdateProfile } from "@/lib/api/hooks/use-auth";
import { AccountSettingsForm, AccountShell } from "@/components/account";
import { PageBreadcrumbs } from "@/components/layout/breadcrumbs";

function AccountSettingsPageView() {
  const { isLoading } = useAuth();
  const { data: user } = useCurrentUser();
  const updateProfile = useUpdateProfile();

  const handleSave = async (values: {
    firstName: string;
    lastName: string;
    phone: string;
  }) => {
    try {
      await updateProfile.mutateAsync({
        first_name: values.firstName,
        last_name: values.lastName,
        phone: values.phone,
      });
      toast.success("Settings saved");
    } catch {
      toast.error("Could not save settings");
    }
  };

  if (isLoading || !user) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <Loader2 className="size-8 animate-spin text-brand-blue" />
      </div>
    );
  }

  return (
    <>
      <PageBreadcrumbs items={getAccountBreadcrumbs("Account Settings")} />
      <AccountShell title="Account settings" description="Update your profile and contact details.">
        <AccountSettingsForm
          initialValues={{
            firstName: user.first_name,
            lastName: user.last_name,
            company: user.organization?.trading_name ?? user.organization?.legal_name ?? "",
            email: user.email,
            phone: user.phone ?? "",
          }}
          onSave={handleSave}
          isSaving={updateProfile.isPending}
        />
      </AccountShell>
    </>
  );
}

export { AccountSettingsPageView };
