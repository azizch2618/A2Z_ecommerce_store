import type { ProductStockStatus } from "@/types/product";

export interface WishlistItem {
  id: string;
  productId: string;
  variantId?: string;
  slug: string;
  name: string;
  brand: string;
  sku: string;
  priceIncGst: number;
  tradePriceIncGst?: number;
  imageSrc: string;
  imageAlt: string;
  href: string;
  stock: ProductStockStatus;
}
