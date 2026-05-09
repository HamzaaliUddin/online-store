from django_filters import rest_framework as filters

from .models import Brand, Collection, Product


class BrandFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Brand
        fields = ["name", "is_active"]


class CollectionFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Collection
        fields = ["name", "is_active"]


class ProductFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    in_stock = filters.BooleanFilter(method="filter_in_stock")

    def filter_in_stock(self, qs, name, value):
        return qs.filter(stock__gt=0) if value else qs.filter(stock=0)

    class Meta:
        model = Product
        fields = ["status", "is_featured", "brand", "collections", "vendor"]
