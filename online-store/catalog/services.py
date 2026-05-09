from django.db import transaction
from rest_framework.exceptions import PermissionDenied

from ecommerce.users.models import Role, User

from .models import Product


class ProductService:
    @staticmethod
    @transaction.atomic
    def create_product(vendor: User, validated_data: dict) -> Product:
        if vendor.role not in (Role.VENDOR, Role.ADMIN, Role.SUPERADMIN):
            raise PermissionDenied("Only vendors or admins can create products.")
        collections = validated_data.pop("collections", [])
        product = Product(vendor=vendor, **validated_data)
        product.full_clean()
        product.save()
        if collections:
            product.collections.set(collections)
        return product

    @staticmethod
    @transaction.atomic
    def update_product(product: Product, validated_data: dict) -> Product:
        collections = validated_data.pop("collections", None)
        for field, value in validated_data.items():
            setattr(product, field, value)
        product.full_clean()
        product.save()
        if collections is not None:
            product.collections.set(collections)
        return product

    @staticmethod
    def visible_queryset_for(user: User):
        qs = Product.objects.select_related("vendor", "brand").prefetch_related(
            "collections", "images"
        )
        if not user.is_authenticated:
            return qs.filter(status=Product.Status.ACTIVE)
        if user.role in (Role.ADMIN, Role.SUPERADMIN):
            return qs
        if user.role == Role.VENDOR:
            return qs.filter(vendor=user) | qs.filter(status=Product.Status.ACTIVE)
        return qs.filter(status=Product.Status.ACTIVE)
