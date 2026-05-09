from django.contrib import admin

from .models import Brand, Collection, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "vendor", "brand", "price", "stock", "status", "is_featured")
    list_filter = ("status", "is_featured", "brand")
    search_fields = ("name", "sku", "vendor__email")
    autocomplete_fields = ("vendor", "brand")
    filter_horizontal = ("collections",)
    inlines = [ProductImageInline]
