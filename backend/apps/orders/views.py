from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CanCheckout, CanManageOrders, IsEmailVerified
from apps.accounts.rbac import PermissionCodename
from apps.accounts.services import PermissionService
from apps.core.exceptions import ConflictError, NotFoundError
from apps.core.pagination import A2ZCursorPagination
from apps.customers.services import CustomerService
from apps.orders.filters import OrderFilter
from apps.orders.models import Cart, Order, Wishlist
from apps.orders.permissions import IsOrderOwnerOrCanViewOrders
from apps.orders.serializers import (
    AddToCartSerializer,
    AddToWishlistSerializer,
    CartSerializer,
    CreateOrderSerializer,
    MergeCartSerializer,
    OrderCancelSerializer,
    OrderDetailSerializer,
    OrderShipSerializer,
    OrderSummarySerializer,
    OrderTrackSerializer,
    TrackOrderSerializer,
    UpdateCartItemSerializer,
    WishlistSerializer,
)
from apps.orders.services import CartService, OrderService, WishlistService


class CartView(APIView):
    permission_classes = [AllowAny]

    def _resolve_cart(self, request) -> Cart:
        customer = None
        if request.user.is_authenticated:
            customer = CustomerService.get_for_user(request.user)
        session_key = request.headers.get("X-Session-Key", "") or None
        return CartService.get_or_create_cart(customer=customer, session_key=session_key)

    def get(self, request):
        cart = self._resolve_cart(request)
        cart = (
            Cart.objects.filter(pk=cart.pk)
            .prefetch_related(
                "items__variant__product__images",
                "items__variant__inventory_levels",
            )
            .first()
        )
        return Response(CartSerializer(cart).data)


class CartItemCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = CustomerService.get_for_user(request.user) if request.user.is_authenticated else None
        session_key = request.headers.get("X-Session-Key", "") or None
        cart = CartService.get_or_create_cart(customer=customer, session_key=session_key)
        cart = CartService.add_item(
            cart,
            serializer.validated_data["variant_id"],
            serializer.validated_data["quantity"],
        )
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    permission_classes = [AllowAny]

    def _resolve_cart(self, request) -> Cart:
        customer = None
        if request.user.is_authenticated:
            customer = CustomerService.get_for_user(request.user)
        session_key = request.headers.get("X-Session-Key", "") or None
        return CartService.get_or_create_cart(customer=customer, session_key=session_key)

    def patch(self, request, public_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = self._resolve_cart(request)
        cart = CartService.update_item_quantity(
            cart, public_id, serializer.validated_data["quantity"]
        )
        return Response(CartSerializer(cart).data)

    def delete(self, request, public_id):
        cart = self._resolve_cart(request)
        cart = CartService.remove_item(cart, public_id)
        return Response(CartSerializer(cart).data)


class CartClearView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        customer = None
        if request.user.is_authenticated:
            customer = CustomerService.get_for_user(request.user)
        session_key = request.headers.get("X-Session-Key", "") or None
        cart = CartService.get_or_create_cart(customer=customer, session_key=session_key)
        cart = CartService.clear(cart)
        return Response(CartSerializer(cart).data)


class CartMergeView(APIView):
    """POST /cart/merge/ — merge guest session cart into authenticated customer cart."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MergeCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = CustomerService.get_for_user(request.user)
        cart = CartService.merge_guest_cart(
            customer=customer,
            session_key=serializer.validated_data["session_key"],
        )
        cart = (
            Cart.objects.filter(pk=cart.pk)
            .prefetch_related(
                "items__variant__product__images",
                "items__variant__inventory_levels",
            )
            .first()
        )
        return Response(CartSerializer(cart).data)


class OrderListCreateView(generics.ListCreateAPIView):
    pagination_class = A2ZCursorPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), CanCheckout(), IsEmailVerified()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return OrderSummarySerializer
        return CreateOrderSerializer

    def get_queryset(self):
        if PermissionService.has_permission(
            self.request.user, PermissionCodename.ORDERS_VIEW
        ):
            return OrderService.staff_orders_queryset()
        customer = CustomerService.get_for_user(self.request.user)
        if not customer:
            return Order.objects.none()
        return OrderService.customer_orders_queryset(customer)

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        customer = CustomerService.get_for_user(request.user)
        if not customer:
            return Response({"detail": "Customer profile required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(public_id=data["cart_id"])
        except Cart.DoesNotExist as exc:
            raise NotFoundError("Cart not found.") from exc

        session_key = request.headers.get("X-Session-Key", "") or None
        if cart.customer_id:
            if cart.customer_id != customer.id:
                raise ConflictError("Cart does not belong to this customer.")
        elif session_key:
            if cart.session_key != session_key:
                raise ConflictError("Cart does not belong to this session.")
            cart.customer = customer
            cart.session_key = ""
            cart.save(update_fields=["customer", "session_key", "updated_at"])
        else:
            raise ConflictError("Cart ownership could not be verified.")

        order = OrderService.create_from_cart(
            cart=cart,
            customer=customer,
            billing_address=data["billing_address"],
            shipping_address=data.get("shipping_address"),
            shipping_method_id=str(data["shipping_method_id"]),
            payment_method=data["payment_method"],
            email=data.get("email") or request.user.email,
            po_number=data.get("po_number", ""),
            customer_notes=data.get("customer_notes", ""),
        )
        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrCanViewOrders]
    lookup_field = "public_id"

    def get_queryset(self):
        if PermissionService.has_permission(
            self.request.user, PermissionCodename.ORDERS_VIEW
        ):
            return OrderService.staff_orders_queryset()
        customer = CustomerService.get_for_user(self.request.user)
        if not customer:
            return Order.objects.none()
        return OrderService.customer_orders_queryset(customer)


class OrderTrackView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TrackOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.track_order(
            order_number=serializer.validated_data["order_number"],
            email=serializer.validated_data["email"],
        )
        return Response(OrderTrackSerializer(order).data)


class _StaffOrderActionView(APIView):
    permission_classes = [CanManageOrders]

    def get_order(self, public_id):
        return OrderService.get_by_public_id(public_id)


class OrderPackView(_StaffOrderActionView):
    """POST /orders/{id}/pack/"""

    def post(self, request, public_id):
        from apps.core.audit import log_operation
        from apps.core.models import OperationalAuditLog

        order = self.get_order(public_id)
        order = OrderService.mark_packed(order)
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.ORDERS,
            action="pack",
            resource_type="order",
            resource_id=order.public_id,
        )
        return Response(OrderDetailSerializer(order).data)


class OrderShipView(_StaffOrderActionView):
    """POST /orders/{id}/ship/"""

    def post(self, request, public_id):
        from apps.core.audit import log_operation
        from apps.core.models import OperationalAuditLog

        order = self.get_order(public_id)
        serializer = OrderShipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        OrderService.mark_shipped(order, **serializer.validated_data)
        order.refresh_from_db()
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.ORDERS,
            action="ship",
            resource_type="order",
            resource_id=order.public_id,
            details=serializer.validated_data,
        )
        return Response(OrderDetailSerializer(order).data)


class OrderDeliverView(_StaffOrderActionView):
    """POST /orders/{id}/deliver/"""

    def post(self, request, public_id):
        from apps.core.audit import log_operation
        from apps.core.models import OperationalAuditLog

        order = self.get_order(public_id)
        order = OrderService.mark_delivered(order)
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.ORDERS,
            action="deliver",
            resource_type="order",
            resource_id=order.public_id,
        )
        return Response(OrderDetailSerializer(order).data)


class OrderCancelView(_StaffOrderActionView):
    """POST /orders/{id}/cancel/"""

    def post(self, request, public_id):
        from apps.core.audit import log_operation
        from apps.core.models import OperationalAuditLog

        order = self.get_order(public_id)
        serializer = OrderCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.cancel_order(order, reason=serializer.validated_data["reason"])
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.ORDERS,
            action="cancel",
            resource_type="order",
            resource_id=order.public_id,
            details={"reason": serializer.validated_data["reason"]},
        )
        return Response(OrderDetailSerializer(order).data)


class OrderRefundView(_StaffOrderActionView):
    """POST /orders/{id}/refund/"""

    def post(self, request, public_id):
        order = self.get_order(public_id)
        serializer = OrderCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.refund_order(
            order,
            reason=serializer.validated_data.get("reason", ""),
            user=request.user,
        )
        return Response(OrderDetailSerializer(order).data)


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def _prefetch(self, wishlist: Wishlist) -> Wishlist:
        return (
            Wishlist.objects.filter(pk=wishlist.pk)
            .prefetch_related(
                "items__variant__product__images",
                "items__variant__product__brand",
                "items__variant__inventory_levels",
            )
            .first()
        )

    def _get_wishlist(self, request) -> Wishlist:
        customer = CustomerService.get_for_user(request.user)
        if not customer:
            raise NotFoundError("Customer profile not found.")
        wishlist = WishlistService.get_or_create_wishlist(customer)
        return self._prefetch(wishlist)

    def get(self, request):
        wishlist = self._get_wishlist(request)
        return Response(WishlistSerializer(wishlist).data)


class WishlistItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToWishlistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = CustomerService.get_for_user(request.user)
        if not customer:
            raise NotFoundError("Customer profile not found.")
        wishlist = WishlistService.get_or_create_wishlist(customer)
        wishlist = WishlistService.add_item(
            wishlist,
            serializer.validated_data["variant_id"],
            serializer.validated_data.get("quantity", 1),
        )
        wishlist = WishlistView()._prefetch(wishlist)
        return Response(WishlistSerializer(wishlist).data, status=status.HTTP_201_CREATED)


class WishlistItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, public_id):
        customer = CustomerService.get_for_user(request.user)
        if not customer:
            raise NotFoundError("Customer profile not found.")
        wishlist = WishlistService.get_or_create_wishlist(customer)
        wishlist = WishlistService.remove_item(wishlist, public_id)
        wishlist = WishlistView()._prefetch(wishlist)
        return Response(WishlistSerializer(wishlist).data)
