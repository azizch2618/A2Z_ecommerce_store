import type { Cart as ApiCart } from "@/lib/api/types/cart";
import type { CartItem as UiCartItem } from "@/types/cart";

export function mapApiCartToUiItems(cart: ApiCart): UiCartItem[] {
  return cart.items.map((item) => ({
    id: item.id,
    productId: item.variant_id,
    slug: item.sku.toLowerCase(),
    brand: item.product_name.split(" ")[0] ?? "",
    name: item.product_name,
    sku: item.sku,
    priceValue: item.price.amount_inc_gst_cents / 100,
    quantity: item.quantity,
    imageSrc: item.image_url ?? "/images/product-placeholder.png",
    imageAlt: item.product_name,
    href: `/products?search=${encodeURIComponent(item.sku)}`,
    maxQuantity: Math.max(item.stock.quantity_available, item.quantity),
  }));
}
