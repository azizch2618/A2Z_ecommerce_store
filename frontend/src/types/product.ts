export type ProductStockStatus =
  | "in_stock"
  | "low_stock"
  | "back_order"
  | "out_of_stock";

export interface ListingProduct {
  id: string;
  brand: string;
  brandId?: string;
  name: string;
  sku: string;
  price: string;
  priceValue?: number;
  tradePrice?: string;
  stock: ProductStockStatus;
  badge?: string;
  href: string;
  description?: string;
  highlights?: string[];
  rating?: number;
  reviewCount?: number;
  imageSrc?: string;
  imageAlt?: string;
  defaultVariantId?: string;
}

export function getProductStock(product: {
  stock: "in_stock" | "low_stock" | "out_of_stock";
  availability?: ProductStockStatus;
}): ProductStockStatus {
  if (product.availability) {
    return product.availability;
  }
  return product.stock;
}
