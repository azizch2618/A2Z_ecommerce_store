import { FileText, ShieldCheck, Truck } from "lucide-react";

import { cn } from "@/lib/utils";

export interface CartTrustRowProps {
  className?: string;
}

const trustItems = [
  {
    icon: Truck,
    label: "Australian stock",
    detail: "Ships from local warehouses",
  },
  {
    icon: FileText,
    label: "Tax invoice",
    detail: "ABN & GST on every order",
  },
  {
    icon: ShieldCheck,
    label: "Secure checkout",
    detail: "Trade & card payments",
  },
] as const;

function CartTrustRow({ className }: CartTrustRowProps) {
  return (
    <ul
      className={cn(
        "grid gap-3 sm:grid-cols-3 sm:gap-4",
        className
      )}
    >
      {trustItems.map(({ icon: Icon, label, detail }) => (
        <li
          key={label}
          className="flex items-start gap-3 rounded-lg border border-border/80 bg-muted/30 px-4 py-3"
        >
          <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-brand-blue-light text-brand-blue">
            <Icon className="size-4" aria-hidden />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-brand-navy">{label}</p>
            <p className="text-xs text-muted-foreground">{detail}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}

export { CartTrustRow };
