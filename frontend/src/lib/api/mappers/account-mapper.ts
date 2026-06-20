import type { AccountOrder, SavedAddress } from "@/types/account";
import type { ApiAddress } from "@/lib/api/types/common";
import type { OrderSummary } from "@/lib/api/types/order";

function mapOrderStatus(status: string): AccountOrder["status"] {
  switch (status) {
    case "pending":
    case "paid":
    case "packed":
      return "processing";
    case "shipped":
      return "shipped";
    case "delivered":
      return "delivered";
    case "cancelled":
      return "cancelled";
    default:
      return "processing";
  }
}

export function mapApiOrderToAccountOrder(order: OrderSummary): AccountOrder {
  return {
    id: order.id,
    orderNumber: order.order_number,
    date: order.placed_at,
    status: mapOrderStatus(order.status),
    totalIncGst: order.total_inc_gst_cents / 100,
    itemCount: order.item_count,
  };
}

export function mapApiAddressToSavedAddress(address: ApiAddress): SavedAddress {
  return {
    id: address.id ?? "",
    label: address.label ?? "Address",
    line1: address.line1,
    line2: address.line2 ?? undefined,
    city: address.suburb,
    state: address.state,
    postcode: address.postcode,
    country: address.country ?? "Australia",
    isDefault: Boolean(address.is_default_shipping || address.is_default_billing),
  };
}
