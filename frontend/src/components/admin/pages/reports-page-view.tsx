"use client";

import { FileSpreadsheet, FileText, Table2 } from "lucide-react";
import { toast } from "sonner";

import { AdminCard } from "@/components/admin/shared/admin-card";
import { AdminListPage } from "@/components/admin/shared/admin-list-page";
import { useAdminReports, useExportReport } from "@/lib/api/admin/hooks";
import { Button } from "@/components/ui/button";

function downloadReport(filename: string, content: string, format: "pdf" | "excel" | "csv") {
  const mime =
    format === "csv"
      ? "text/csv;charset=utf-8"
      : format === "excel"
        ? "application/vnd.ms-excel"
        : "application/pdf";
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function ReportsPageView() {
  const { data: reports, isLoading, isError } = useAdminReports();
  const exportReport = useExportReport();

  const handleExport = (reportId: string, format: "pdf" | "excel" | "csv") => {
    exportReport.mutate(
      { reportId, format },
      {
        onSuccess: (result: { filename: string; content: string }) => {
          downloadReport(result.filename, result.content, format);
          toast.success(`Downloaded ${result.filename}`);
        },
        onError: () => toast.error("Export failed"),
      }
    );
  };

  return (
    <AdminListPage
      title="Reports"
      description="Generate and export business reports for accounting and operations."
      isLoading={isLoading}
      isError={isError}
    >
      <div className="grid gap-4 md:grid-cols-2">
        {reports?.map((report) => (
          <AdminCard key={report.id} title={report.name} description={report.description}>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport(report.id, "pdf")}
                disabled={exportReport.isPending}
              >
                <FileText className="mr-2 size-4" />
                PDF
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport(report.id, "excel")}
                disabled={exportReport.isPending}
              >
                <FileSpreadsheet className="mr-2 size-4" />
                Excel
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleExport(report.id, "csv")}
                disabled={exportReport.isPending}
              >
                <Table2 className="mr-2 size-4" />
                CSV
              </Button>
            </div>
          </AdminCard>
        ))}
      </div>
    </AdminListPage>
  );
}

export { ReportsPageView };
