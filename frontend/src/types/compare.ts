import type { ProductStockStatus } from "@/types/product";

export interface CompareProductSpecs {
  [key: string]: string;
}

export interface CompareProduct {
  id: string;
  slug: string;
  name: string;
  brand: string;
  sku: string;
  priceIncGst: number;
  tradePriceIncGst?: number;
  rating?: number;
  reviewCount?: number;
  stock: ProductStockStatus;
  imageSrc: string;
  imageAlt: string;
  href: string;
  specs: CompareProductSpecs;
}

export type CompareSpecKey = string;
