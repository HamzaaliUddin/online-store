from django_filters import rest_framework as filters

from .models import Order


class OrderFilter(filters.FilterSet):
    min_total = filters.NumberFilter(field_name="total", lookup_expr="gte")
    max_total = filters.NumberFilter(field_name="total", lookup_expr="lte")
    placed_after = filters.DateTimeFilter(field_name="placed_at", lookup_expr="gte")
    placed_before = filters.DateTimeFilter(field_name="placed_at", lookup_expr="lte")

    class Meta:
        model = Order
        fields = ["status", "payment_status", "customer"]
