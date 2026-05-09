from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "vendor", "product_name", "unit_price",
                       "quantity", "line_total")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer", "status", "payment_status",
                    "total", "placed_at")
    list_filter = ("status", "payment_status")
    search_fields = ("reference", "customer__email")
    readonly_fields = ("reference", "subtotal", "total", "placed_at",
                       "created_at", "updated_at")
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product_name", "vendor", "unit_price",
                    "quantity", "line_total")
    search_fields = ("order__reference", "product_name", "vendor__email")
