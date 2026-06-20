import type { PriceBlock, StockBlock } from "./common";

export interface WishlistItem {
  id: string;
  variant_id: string;
  product_id: string;
  product_slug: string;
  sku: string;
  product_name: string;
  variant_name: string | null;
  brand: string;
  image_url: string | null;
  desired_quantity: number;
  price: PriceBlock;
  stock: StockBlock;
}

export interface Wishlist {
  id: string;
  items: WishlistItem[];
  item_count: number;
  updated_at: string;
}

export interface AddToWishlistPayload {
  variant_id: string;
  quantity?: number;
}
