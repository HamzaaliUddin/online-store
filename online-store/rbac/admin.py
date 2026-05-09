from django.contrib import admin

from .models import Module, RoleModulePermission


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")


@admin.register(RoleModulePermission)
class RoleModulePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "module", "can_view", "can_create", "can_update", "can_delete")
    list_filter = ("role", "module")
    search_fields = ("module__code", "module__name")
