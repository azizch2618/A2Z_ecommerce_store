import { apiDelete, apiGet, apiPatch, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type {
  AddToCartPayload,
  ApplyCouponPayload,
  Cart,
  MergeCartPayload,
  UpdateCartItemPayload,
} from "../types/cart";

/** Current cart (authenticated or guest session) */
export async function fetchCart(): Promise<Cart> {
  return apiGet<Cart>(API_ENDPOINTS.cart.root);
}

/** Add variant to cart or increment quantity */
export async function addToCart(payload: AddToCartPayload): Promise<Cart> {
  return apiPost<Cart, AddToCartPayload>(
    API_ENDPOINTS.cart.items,
    payload
  );
}

/** Update line item quantity */
export async function updateCartItem(
  itemId: string,
  payload: UpdateCartItemPayload
): Promise<Cart> {
  return apiPatch<Cart, UpdateCartItemPayload>(
    API_ENDPOINTS.cart.item(itemId),
    payload
  );
}

/** Remove line item */
export async function removeCartItem(itemId: string): Promise<Cart> {
  return apiDelete<Cart>(API_ENDPOINTS.cart.item(itemId));
}

/** Clear all cart items */
export async function clearCart(): Promise<Cart> {
  return apiPost<Cart>(API_ENDPOINTS.cart.clear);
}

/** Apply discount coupon */
export async function applyCartCoupon(
  payload: ApplyCouponPayload
): Promise<Cart> {
  return apiPost<Cart, ApplyCouponPayload>(
    API_ENDPOINTS.cart.coupon,
    payload
  );
}

/** Remove applied coupon */
export async function removeCartCoupon(): Promise<Cart> {
  return apiDelete<Cart>(API_ENDPOINTS.cart.coupon);
}

/** Merge guest cart into user cart after login */
export async function mergeGuestCart(
  payload: MergeCartPayload
): Promise<Cart> {
  return apiPost<Cart, MergeCartPayload>(
    API_ENDPOINTS.cart.merge,
    payload
  );
}
