import { throwAdminApiUnavailable } from "./admin-api-unavailable";
import type { TradeApplication, TradeStatus } from "./types";

export async function updateTradeApplicationStatus(
  id: string,
  status: TradeStatus
): Promise<TradeApplication> {
  void id;
  void status;
  return throwAdminApiUnavailable("trade application updates");
}

export async function exportReport(
  reportId: string,
  format: "pdf" | "excel" | "csv"
): Promise<{ url: string; filename: string }> {
  void reportId;
  void format;
  return throwAdminApiUnavailable("report export");
}
