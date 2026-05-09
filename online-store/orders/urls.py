from django.urls import path

from .views import (
    AdminOrderListView,
    OrderCancelView,
    OrderDetailView,
    OrderListCreateView,
    OrderStatusUpdateView,
)

app_name = "orders"

urlpatterns = [
    path("", OrderListCreateView.as_view(), name="orders"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("<int:pk>/cancel/", OrderCancelView.as_view(), name="order-cancel"),
    path("<int:pk>/status/", OrderStatusUpdateView.as_view(), name="order-status"),
    path("admin/", AdminOrderListView.as_view(), name="admin-orders"),
]
