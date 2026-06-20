import type { WishlistItem } from "@/types/wishlist";
import type { WishlistItem as ApiWishlistItem } from "@/lib/api/types/wishlist";

function mapStockStatus(status: string): WishlistItem["stock"] {
  if (status === "in_stock" || status === "low_stock" || status === "out_of_stock") {
    return status;
  }
  if (status === "backorder" || status === "back_order") {
    return "back_order";
  }
  return "in_stock";
}

export function mapApiWishlistItemToUi(item: ApiWishlistItem): WishlistItem {
  return {
    id: item.id,
    productId: item.product_id,
    slug: item.product_slug,
    name: item.product_name,
    brand: item.brand,
    sku: item.sku,
    priceIncGst: item.price.amount_inc_gst_cents / 100,
    tradePriceIncGst: item.price.is_trade_price
      ? item.price.amount_inc_gst_cents / 100
      : undefined,
    imageSrc: item.image_url ?? "",
    imageAlt: item.product_name,
    href: `/products/${item.product_slug}`,
    stock: mapStockStatus(item.stock.status),
    variantId: item.variant_id,
  };
}
