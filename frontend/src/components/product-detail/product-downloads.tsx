import { Download, FileText, HardDrive } from "lucide-react";

import type { ProductDownload } from "@/config/product-detail";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export interface ProductDownloadsProps {
  downloads: ProductDownload[];
  className?: string;
}

const typeIcons = {
  PDF: FileText,
  ZIP: HardDrive,
  Firmware: HardDrive,
};

function ProductDownloads({ downloads, className }: ProductDownloadsProps) {
  if (downloads.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        No downloads available for this product.
      </p>
    );
  }

  return (
    <ul className={cn("divide-y divide-border rounded-xl border border-border", className)}>
      {downloads.map((file) => {
        const Icon = typeIcons[file.type];
        return (
          <li key={file.id}>
            <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between sm:p-5">
              <div className="flex items-start gap-3">
                <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-brand-blue-light text-brand-blue">
                  <Icon className="size-5" />
                </div>
                <div>
                  <p className="font-medium text-brand-navy">{file.title}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-2">
                    <Badge variant="outline" className="text-[10px] uppercase">
                      {file.type}
                    </Badge>
                    <span className="text-xs text-muted-foreground">{file.size}</span>
                  </div>
                </div>
              </div>
              <Button
                asChild
                variant="outline"
                size="sm"
                className="w-full gap-2 sm:w-auto"
              >
                <a href={file.href} download>
                  <Download className="size-4" />
                  Download
                </a>
              </Button>
            </div>
          </li>
        );
      })}
    </ul>
  );
}

export { ProductDownloads };
