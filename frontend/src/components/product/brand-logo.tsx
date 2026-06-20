import { getBrandImage } from "@/config/visual-assets";
import { RemoteImage } from "@/components/ui/remote-image";
import { cn } from "@/lib/utils";

export interface BrandLogoProps {
  brandId: string;
  brandName: string;
  size?: "xs" | "sm" | "md";
  className?: string;
}

const sizeClasses = {
  xs: "size-5",
  sm: "size-7",
  md: "size-9",
};

function BrandLogo({ brandId, brandName, size = "sm", className }: BrandLogoProps) {
  const image = getBrandImage(brandId);

  return (
    <div
      className={cn(
        "relative shrink-0 overflow-hidden rounded-md border border-border bg-white shadow-sm",
        sizeClasses[size],
        className
      )}
      title={brandName}
    >
      <RemoteImage
        src={image.src}
        alt={`${brandName} logo`}
        fill
        sizes="36px"
        className="object-cover"
      />
    </div>
  );
}

export { BrandLogo };
