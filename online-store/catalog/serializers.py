from rest_framework import serializers

from .models import Brand, Collection, Product, ProductImage


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = (
            "id", "name", "slug", "description", "logo", "is_active",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = (
            "id", "name", "slug", "description", "image", "is_active",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "alt_text", "position")
        read_only_fields = ("id",)


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    vendor_email = serializers.EmailField(source="vendor.email", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    collection_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        required=False,
        source="collections",
        queryset=Collection.objects.all(),
    )
    collections = CollectionSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "sku",
            "description",
            "price",
            "compare_at_price",
            "stock",
            "status",
            "is_featured",
            "vendor",
            "vendor_email",
            "brand",
            "brand_name",
            "collections",
            "collection_ids",
            "images",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "slug",
            "vendor",
            "vendor_email",
            "brand_name",
            "created_at",
            "updated_at",
        )

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be non-negative.")
        return value

    def validate(self, attrs):
        price = attrs.get("price", getattr(self.instance, "price", None))
        compare = attrs.get("compare_at_price",
                            getattr(self.instance, "compare_at_price", None))
        if compare is not None and price is not None and compare < price:
            raise serializers.ValidationError(
                {"compare_at_price": "Compare-at price must be >= price."}
            )
        return attrs
