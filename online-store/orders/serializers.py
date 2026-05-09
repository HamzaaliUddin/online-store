from decimal import Decimal

from rest_framework import serializers

from ecommerce.catalog.models import Product

from .models import Order, OrderItem


class OrderItemReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product",
            "vendor",
            "product_name",
            "unit_price",
            "quantity",
            "line_total",
        )
        read_only_fields = fields


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(status=Product.Status.ACTIVE)
    )
    quantity = serializers.IntegerField(min_value=1)


class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "reference",
            "customer",
            "customer_email",
            "status",
            "payment_status",
            "subtotal",
            "shipping_fee",
            "tax",
            "total",
            "shipping_address_line1",
            "shipping_address_line2",
            "shipping_city",
            "shipping_state",
            "shipping_postal_code",
            "shipping_country",
            "contact_phone",
            "notes",
            "placed_at",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = (
            "shipping_address_line1",
            "shipping_address_line2",
            "shipping_city",
            "shipping_state",
            "shipping_postal_code",
            "shipping_country",
            "contact_phone",
            "notes",
            "shipping_fee",
            "tax",
            "items",
        )

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("At least one item is required.")
        seen = set()
        for item in items:
            pid = item["product"].pk
            if pid in seen:
                raise serializers.ValidationError(
                    f"Duplicate product in order: {pid}"
                )
            seen.add(pid)
            if item["product"].stock < item["quantity"]:
                raise serializers.ValidationError(
                    f"Insufficient stock for product {item['product'].name}."
                )
        return items

    def validate_shipping_fee(self, value):
        if value < 0:
            raise serializers.ValidationError("Shipping fee must be non-negative.")
        return value

    def validate_tax(self, value):
        if value < 0:
            raise serializers.ValidationError("Tax must be non-negative.")
        return value


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("status", "payment_status")

    def validate_status(self, value):
        instance = self.instance
        if instance and instance.status == Order.Status.DELIVERED and value != Order.Status.REFUNDED:
            raise serializers.ValidationError(
                "Delivered orders can only transition to refunded."
            )
        return value
