from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from ecommerce.common.permissions import (
    HasModulePermission,
    IsAdminOrSuperAdmin,
)
from ecommerce.common.responses import APIResponse
from ecommerce.users.models import Role

from .filters import BrandFilter, CollectionFilter, ProductFilter
from .models import Brand, Collection, Product
from .serializers import (
    BrandSerializer,
    CollectionSerializer,
    ProductSerializer,
)
from .services import ProductService


class BrandListCreateView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "brands"
    filterset_class = BrandFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]


class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "brands"


class CollectionListCreateView(generics.ListCreateAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "collections"
    filterset_class = CollectionFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]


class CollectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "collections"


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "products"
    filterset_class = ProductFilter
    search_fields = ["name", "sku", "description", "brand__name"]
    ordering_fields = ["price", "created_at", "name"]

    def get_queryset(self):
        return ProductService.visible_queryset_for(self.request.user)

    def perform_create(self, serializer):
        product = ProductService.create_product(
            self.request.user, serializer.validated_data
        )
        serializer.instance = product


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, HasModulePermission]
    module_code = "products"

    def get_queryset(self):
        return ProductService.visible_queryset_for(self.request.user)

    def _ensure_owner_or_admin(self):
        product = self.get_object()
        user = self.request.user
        if user.role in (Role.ADMIN, Role.SUPERADMIN):
            return product
        if product.vendor_id != user.id:
            raise PermissionDenied("You can only modify your own products.")
        return product

    def update(self, request, *args, **kwargs):
        self._ensure_owner_or_admin()
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        product = ProductService.update_product(
            serializer.instance, serializer.validated_data
        )
        serializer.instance = product

    def destroy(self, request, *args, **kwargs):
        self._ensure_owner_or_admin()
        return super().destroy(request, *args, **kwargs)


class PublicProductListView(generics.ListAPIView):
    """Customer-facing list (active products only)."""

    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ["name", "sku", "description", "brand__name"]
    ordering_fields = ["price", "created_at", "name"]

    def get_queryset(self):
        return (
            Product.objects.filter(status=Product.Status.ACTIVE)
            .select_related("vendor", "brand")
            .prefetch_related("collections", "images")
        )


class MyProductsView(generics.ListAPIView):
    """Vendor-only: products owned by the requesting vendor."""

    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ["name", "sku"]
    ordering_fields = ["price", "created_at"]

    def get_queryset(self):
        if self.request.user.role != Role.VENDOR:
            raise PermissionDenied("Vendor role required.")
        return (
            Product.objects.filter(vendor=self.request.user)
            .select_related("brand")
            .prefetch_related("collections", "images")
        )


class AdminProductModerateView(generics.UpdateAPIView):
    """Admin: change product status (active/archived/draft)."""

    permission_classes = [IsAdminOrSuperAdmin]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def patch(self, request, *args, **kwargs):
        product = self.get_object()
        new_status = request.data.get("status")
        if new_status not in Product.Status.values:
            return APIResponse.error("Invalid status.")
        product.status = new_status
        product.save(update_fields=["status", "updated_at"])
        return APIResponse.success(
            ProductSerializer(product).data, message="Status updated."
        )
