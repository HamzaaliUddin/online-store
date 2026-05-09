from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from ecommerce.common.permissions import HasModulePermission, IsAdminOrSuperAdmin
from ecommerce.common.responses import APIResponse
from ecommerce.users.models import Role

from .filters import OrderFilter
from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderReadSerializer,
    OrderStatusUpdateSerializer,
)
from .services import OrderService


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "orders"
    filterset_class = OrderFilter
    search_fields = ["reference", "customer__email", "shipping_city"]
    ordering_fields = ["created_at", "placed_at", "total", "status"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderReadSerializer

    def get_queryset(self):
        return OrderService.visible_queryset_for(self.request.user)

    def create(self, request, *args, **kwargs):
        if request.user.role != Role.CUSTOMER:
            raise PermissionDenied("Only customers can place orders.")
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.create_order(request.user, serializer.validated_data)
        return APIResponse.created(
            OrderReadSerializer(order).data, message="Order placed."
        )


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "orders"
    serializer_class = OrderReadSerializer

    def get_queryset(self):
        return OrderService.visible_queryset_for(self.request.user)


class OrderCancelView(generics.GenericAPIView):
    """Customer cancels their own pending order."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderReadSerializer

    def post(self, request, pk):
        order = Order.objects.filter(pk=pk).first()
        if order is None:
            return APIResponse.error("Order not found.", status=404)
        if order.customer_id != request.user.id and request.user.role not in (
            Role.ADMIN,
            Role.SUPERADMIN,
        ):
            raise PermissionDenied("Not your order.")
        if order.status not in (Order.Status.PENDING, Order.Status.PAID):
            return APIResponse.error(
                "Only pending or paid orders can be cancelled."
            )
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return APIResponse.success(
            OrderReadSerializer(order).data, message="Order cancelled."
        )


class OrderStatusUpdateView(generics.UpdateAPIView):
    """Admin/vendor updates order status. Vendors limited to their own items."""

    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "orders"
    serializer_class = OrderStatusUpdateSerializer
    queryset = Order.objects.all()

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        if user.role == Role.VENDOR and not order.items.filter(vendor=user).exists():
            raise PermissionDenied("Order does not contain your products.")
        partial = kwargs.pop("partial", False)
        serializer = OrderStatusUpdateSerializer(
            instance=order, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        order = OrderService.update_status(order, serializer.validated_data)
        return APIResponse.success(
            OrderReadSerializer(order).data, message="Order status updated."
        )


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperAdmin]
    serializer_class = OrderReadSerializer
    filterset_class = OrderFilter
    search_fields = ["reference", "customer__email"]
    ordering_fields = ["created_at", "total", "status"]
    queryset = (
        Order.objects.select_related("customer")
        .prefetch_related("items", "items__product")
        .all()
    )
