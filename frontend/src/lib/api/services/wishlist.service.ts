import { apiDelete, apiGet, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import type { AddToWishlistPayload, Wishlist } from "../types/wishlist";

export async function fetchWishlist(): Promise<Wishlist> {
  return apiGet<Wishlist>(API_ENDPOINTS.wishlist.root);
}

export async function addToWishlist(payload: AddToWishlistPayload): Promise<Wishlist> {
  return apiPost<Wishlist, AddToWishlistPayload>(
    API_ENDPOINTS.wishlist.items,
    payload
  );
}

export async function removeWishlistItem(itemId: string): Promise<Wishlist> {
  return apiDelete<Wishlist>(API_ENDPOINTS.wishlist.item(itemId));
}
