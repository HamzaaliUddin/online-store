from django.contrib import admin

from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "placement", "position", "is_active", "starts_at", "ends_at")
    list_filter = ("placement", "is_active")
    search_fields = ("title", "subtitle")
    ordering = ("placement", "position")
