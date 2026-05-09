from django.db import transaction

from .catalog import seed_catalog
from .rbac import seed_rbac
from .users import DEFAULT_PASSWORD, seed_users


@transaction.atomic
def run_seed():
    users = seed_users()
    seed_rbac()
    brands, collections, products = seed_catalog(users)

    return {
        "users": users,
        "brands": brands,
        "collections": collections,
        "products": products,
        "default_password": DEFAULT_PASSWORD,
    }
