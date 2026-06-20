export interface AccountDashboardStats {
  totalOrders: number;
  activeOrders: number;
  wishlistItems: number;
  savedQuotes: number;
}

export interface AccountOrder {
  id: string;
  orderNumber: string;
  date: string;
  status: "processing" | "shipped" | "delivered" | "cancelled";
  totalIncGst: number;
  itemCount: number;
}

export interface SavedAddress {
  id: string;
  label: string;
  line1: string;
  line2?: string;
  city: string;
  state: string;
  postcode: string;
  country: string;
  isDefault: boolean;
}

export interface SavedQuote {
  id: string;
  quoteNumber: string;
  title: string;
  date: string;
  totalIncGst: number;
  status: "draft" | "sent" | "accepted" | "expired" | "pending_approval" | "rejected" | "converted";
  expiresAt: string;
}
