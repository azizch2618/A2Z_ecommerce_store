import type { ProductSpecification } from "@/config/product-detail";
import { cn } from "@/lib/utils";
import {
  Table,
  TableBody,
  TableCell,
  TableRow,
} from "@/components/ui/table";

export interface ProductSpecificationsProps {
  specifications: ProductSpecification[];
  className?: string;
}

function ProductSpecifications({
  specifications,
  className,
}: ProductSpecificationsProps) {
  if (specifications.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Specifications are not available for this product.
      </p>
    );
  }

  return (
    <div className={cn("space-y-8", className)}>
      {specifications.map((group) => (
        <div key={group.group}>
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-[0.12em] text-brand-navy">
            {group.group}
          </h3>
          <div className="overflow-hidden rounded-xl border border-border">
            <Table>
              <TableBody>
                {group.items.map((item, index) => (
                  <TableRow
                    key={item.label}
                    className={cn(index % 2 === 0 && "bg-neutral-50/80")}
                  >
                    <TableCell className="w-[40%] py-3.5 font-medium text-brand-navy sm:w-1/3">
                      {item.label}
                    </TableCell>
                    <TableCell className="py-3.5 text-muted-foreground">
                      {item.value}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      ))}
    </div>
  );
}

export { ProductSpecifications };
