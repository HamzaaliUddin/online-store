from ecommerce.rbac.services import RBACService


def seed_rbac():
    RBACService.bootstrap_default_modules_and_permissions()
