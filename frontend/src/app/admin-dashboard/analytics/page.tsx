import type { Metadata } from "next";

import { AnalyticsPageView } from "@/components/admin/pages/analytics-page-view";

export const metadata: Metadata = { title: "Analytics | Admin | A2Z Tools" };

export default function AdminAnalyticsPage() {
  return <AnalyticsPageView />;
}
