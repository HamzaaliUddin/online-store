from rest_framework import serializers

from ecommerce.users.models import Role

from .models import Module, RoleModulePermission


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ("id", "code", "name", "description", "is_active",
                  "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class RoleModulePermissionSerializer(serializers.ModelSerializer):
    module_code = serializers.CharField(source="module.code", read_only=True)
    module_name = serializers.CharField(source="module.name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = RoleModulePermission
        fields = (
            "id",
            "role",
            "role_display",
            "module",
            "module_code",
            "module_name",
            "can_view",
            "can_create",
            "can_update",
            "can_delete",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_role(self, value):
        if value == Role.SUPERADMIN:
            raise serializers.ValidationError(
                "Super admin permissions are implicit and cannot be edited."
            )
        return value

    def validate(self, attrs):
        role = attrs.get("role", getattr(self.instance, "role", None))
        module = attrs.get("module", getattr(self.instance, "module", None))
        qs = RoleModulePermission.objects.filter(role=role, module=module)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Permission already exists for this role and module."
            )
        return attrs
