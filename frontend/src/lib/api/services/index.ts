export {
  fetchProducts,
  fetchProductDetails,
  fetchProductById,
  searchProducts,
  compareProducts,
} from "./products.service";

export {
  fetchCategories,
  fetchCategoryBySlug,
  fetchCategoryProducts,
} from "./categories.service";

export {
  fetchBrands,
  fetchBrandBySlug,
  fetchBrandProducts,
} from "./brands.service";

export {
  fetchCart,
  addToCart,
  updateCartItem,
  removeCartItem,
  clearCart,
  applyCartCoupon,
  removeCartCoupon,
  mergeGuestCart,
} from "./cart.service";

export {
  createOrder,
  fetchOrders,
  fetchOrderById,
  cancelOrder,
  reorder,
} from "./orders.service";

export {
  login,
  register,
  logout,
  fetchCurrentUser,
  updateProfile,
  fetchAddresses,
  createAddress,
  updateAddress,
  deleteAddress,
  forgotPassword,
  verifyEmail,
  resendVerificationEmail,
} from "./auth.service";

export {
  fetchTradeAccount,
  applyForTradeAccount,
  fetchQuotes,
  fetchQuoteById,
} from "./trade-accounts.service";

export {
  fetchInventoryLevels,
  updateReorderLevels,
  fetchStockMovements,
  fetchTransfers,
  fetchValuationSummary,
  fetchLedgerSummary,
  fetchLowStockAlerts,
  fetchInventoryNotifications,
  fetchNotificationUnreadCount,
  acknowledgeNotification,
  stockIn,
  stockOut,
  stockAdjustment,
  stockTransfer,
} from "./inventory.service";
