from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from ecommerce.catalog.models import Brand, Collection, Product
from ecommerce.rbac.services import RBACService
from ecommerce.users.models import Role, User

DEFAULT_PASSWORD = "Password123!"

USERS = [
    {
        "role": Role.SUPERADMIN,
        "email": "superadmin@example.com",
        "first_name": "Super",
        "last_name": "Admin",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "role": Role.ADMIN,
        "email": "admin@example.com",
        "first_name": "Site",
        "last_name": "Admin",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "role": Role.VENDOR,
        "email": "vendor@example.com",
        "first_name": "Vinny",
        "last_name": "Vendor",
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "role": Role.CUSTOMER,
        "email": "customer@example.com",
        "first_name": "Casey",
        "last_name": "Customer",
        "is_staff": False,
        "is_superuser": False,
    },
]

BRANDS = ["Acme", "Globex", "Initech"]
COLLECTIONS = ["Featured", "New Arrivals"]
PRODUCTS = [
    ("Wireless Mouse", "Ergonomic 2.4GHz wireless mouse.", "19.99"),
    ("Mechanical Keyboard", "RGB mechanical keyboard.", "79.99"),
    ("USB-C Hub", "7-in-1 USB-C hub.", "34.50"),
    ("Noise-Cancelling Headphones", "Bluetooth ANC headphones.", "129.00"),
    ("4K Monitor", "27-inch 4K IPS monitor.", "299.99"),
]


class Command(BaseCommand):
    help = "Seed default users, RBAC modules, brands, collections and sample products."

    @transaction.atomic
    def handle(self, *args, **options):
        Product.objects.all().delete()
        Collection.objects.all().delete()
        Brand.objects.all().delete()
        User.objects.all().delete()

        users = {}
        for spec in USERS:
            user = User.objects.create_user(
                email=spec["email"],
                password=DEFAULT_PASSWORD,
                first_name=spec["first_name"],
                last_name=spec["last_name"],
                role=spec["role"],
                is_email_verified=True,
            )
            user.is_staff = spec["is_staff"]
            user.is_superuser = spec["is_superuser"]
            user.save(update_fields=["is_staff", "is_superuser"])
            users[spec["role"]] = user

        RBACService.bootstrap_default_modules_and_permissions()

        brands = [Brand.objects.create(name=name) for name in BRANDS]
        collections = [Collection.objects.create(name=name) for name in COLLECTIONS]

        vendor = users[Role.VENDOR]
        for name, description, price in PRODUCTS:
            product = Product.objects.create(
                name=name,
                description=description,
                price=Decimal(price),
                stock=100,
                vendor=vendor,
                brand=brands[0],
            )
            product.collections.add(collections[0])

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(users)} users, {len(brands)} brands, "
                f"{len(collections)} collections, {len(PRODUCTS)} products. "
                f"Default password: {DEFAULT_PASSWORD}"
            )
        )
