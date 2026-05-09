from django.db import transaction

from ecommerce.users.models import Role


DEFAULT_MODULES = [
    ("users", "Users"),
    ("rbac", "RBAC"),
    ("brands", "Brands"),
    ("collections", "Collections"),
    ("products", "Products"),
    ("banners", "Banners"),
    ("orders", "Orders"),
]

# (role, module_code, view, create, update, delete)
DEFAULT_GRANTS = [
    # Super admin: full
    *[(Role.SUPERADMIN, code, True, True, True, True) for code, _ in DEFAULT_MODULES],
    # Admin: full except users delete & rbac edit (kept for superadmin)
    (Role.ADMIN, "users", True, True, True, False),
    (Role.ADMIN, "rbac", True, False, False, False),
    (Role.ADMIN, "brands", True, True, True, True),
    (Role.ADMIN, "collections", True, True, True, True),
    (Role.ADMIN, "products", True, True, True, True),
    (Role.ADMIN, "banners", True, True, True, True),
    (Role.ADMIN, "orders", True, True, True, True),
    # Vendor: own catalog + own orders (object-level)
    (Role.VENDOR, "brands", True, False, False, False),
    (Role.VENDOR, "collections", True, False, False, False),
    (Role.VENDOR, "products", True, True, True, True),
    (Role.VENDOR, "banners", True, False, False, False),
    (Role.VENDOR, "orders", True, False, True, False),
    # Customer: read catalog, manage own orders
    (Role.CUSTOMER, "brands", True, False, False, False),
    (Role.CUSTOMER, "collections", True, False, False, False),
    (Role.CUSTOMER, "products", True, False, False, False),
    (Role.CUSTOMER, "banners", True, False, False, False),
    (Role.CUSTOMER, "orders", True, True, False, False),
]


class RBACService:
    @staticmethod
    def role_can(role: str, module_code: str, action: str) -> bool:
        from .models import RoleModulePermission

        if role == Role.SUPERADMIN:
            return True
        try:
            perm = RoleModulePermission.objects.select_related("module").get(
                role=role, module__code=module_code, module__is_active=True
            )
        except RoleModulePermission.DoesNotExist:
            return False
        return perm.can(action)

    @staticmethod
    @transaction.atomic
    def bootstrap_default_modules_and_permissions():
        from .models import Module, RoleModulePermission

        for code, name in DEFAULT_MODULES:
            Module.objects.get_or_create(code=code, defaults={"name": name})

        for role, code, view, create_, update, delete in DEFAULT_GRANTS:
            module = Module.objects.get(code=code)
            RoleModulePermission.objects.update_or_create(
                role=role,
                module=module,
                defaults={
                    "can_view": view,
                    "can_create": create_,
                    "can_update": update,
                    "can_delete": delete,
                },
            )
