from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from ecommerce.catalog.models import Product
from ecommerce.users.models import Role, User

from .models import Order, OrderItem


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(customer: User, validated_data: dict) -> Order:
        items_data = validated_data.pop("items")

        order = Order(customer=customer, **validated_data)
        order.save()

        subtotal = Decimal("0.00")
        for item in items_data:
            product: Product = (
                Product.objects.select_for_update().get(pk=item["product"].pk)
            )
            qty = item["quantity"]
            if product.stock < qty:
                raise ValidationError(
                    {"items": f"Insufficient stock for product {product.name}."}
                )
            line_total = product.price * qty
            subtotal += line_total
            OrderItem.objects.create(
                order=order,
                product=product,
                vendor=product.vendor,
                product_name=product.name,
                unit_price=product.price,
                quantity=qty,
            )
            Product.objects.filter(pk=product.pk).update(stock=F("stock") - qty)

        order.subtotal = subtotal
        order.total = subtotal + (order.shipping_fee or 0) + (order.tax or 0)
        order.placed_at = timezone.now()
        order.save(
            update_fields=["subtotal", "total", "placed_at", "updated_at"]
        )
        return order

    @staticmethod
    @transaction.atomic
    def update_status(order: Order, validated_data: dict) -> Order:
        for field, value in validated_data.items():
            setattr(order, field, value)
        order.save(update_fields=["status", "payment_status", "updated_at"])
        return order

    @staticmethod
    def visible_queryset_for(user: User):
        qs = Order.objects.select_related("customer").prefetch_related(
            "items", "items__product"
        )
        if user.role in (Role.ADMIN, Role.SUPERADMIN) or user.is_superuser:
            return qs
        if user.role == Role.VENDOR:
            return qs.filter(items__vendor=user).distinct()
        return qs.filter(customer=user)
