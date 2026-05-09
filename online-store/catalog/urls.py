from django.urls import path

from .views import (
    AdminProductModerateView,
    BrandDetailView,
    BrandListCreateView,
    CollectionDetailView,
    CollectionListCreateView,
    MyProductsView,
    ProductDetailView,
    ProductListCreateView,
    PublicProductListView,
)

app_name = "catalog"

urlpatterns = [
    path("brands/", BrandListCreateView.as_view(), name="brands"),
    path("brands/<int:pk>/", BrandDetailView.as_view(), name="brand-detail"),
    path("collections/", CollectionListCreateView.as_view(), name="collections"),
    path("collections/<int:pk>/", CollectionDetailView.as_view(), name="collection-detail"),
    path("products/", ProductListCreateView.as_view(), name="products"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/public/", PublicProductListView.as_view(), name="products-public"),
    path("products/mine/", MyProductsView.as_view(), name="products-mine"),
    path("products/<int:pk>/moderate/", AdminProductModerateView.as_view(), name="product-moderate"),
]
