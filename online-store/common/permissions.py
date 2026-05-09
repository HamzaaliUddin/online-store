from rest_framework.permissions import BasePermission, SAFE_METHODS


class _RolePermission(BasePermission):
    role: str = ""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and getattr(user, "role", None) == self.role
        )


class IsCustomer(_RolePermission):
    role = "customer"


class IsVendor(_RolePermission):
    role = "vendor"


class IsAdmin(_RolePermission):
    role = "admin"


class IsSuperAdmin(_RolePermission):
    role = "superadmin"


class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "role", None) in ("admin", "superadmin")
        )


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level: the resource owner (vendor) or any admin/superadmin can mutate.
    Override `owner_field` on the view to point at the FK if it isn't `created_by`.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "role", None) in ("admin", "superadmin"):
            return True
        owner_field = getattr(view, "owner_field", "created_by")
        owner = getattr(obj, owner_field, None)
        return owner == user


class HasModulePermission(BasePermission):
    """
    Resolves per-module CRUD access from the rbac app.
    Views must declare `module_code` and (optionally) override action mapping
    via `module_action_map`. Superadmins bypass all checks.
    """

    method_action_map = {
        "GET": "view",
        "HEAD": "view",
        "OPTIONS": "view",
        "POST": "create",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "role", None) == "superadmin" or user.is_superuser:
            return True

        module_code = getattr(view, "module_code", None)
        if not module_code:
            return True

        action = self.method_action_map.get(request.method, "view")

        from ecommerce.rbac.services import RBACService

        return RBACService.role_can(user.role, module_code, action)
