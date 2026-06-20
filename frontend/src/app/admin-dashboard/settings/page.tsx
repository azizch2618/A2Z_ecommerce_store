import type { Metadata } from "next";

import { SettingsPageView } from "@/components/admin/pages/settings-page-view";

export const metadata: Metadata = { title: "Settings | Admin | A2Z Tools" };

export default function AdminSettingsPage() {
  return <SettingsPageView />;
}
