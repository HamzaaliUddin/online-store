from decimal import Decimal

from ecommerce.catalog.models import Brand, Collection, Product
from ecommerce.users.models import Role

BRANDS = ["Acme", "Globex", "Initech"]
COLLECTIONS = ["Featured", "New Arrivals"]
PRODUCTS = [
    ("Wireless Mouse", "Ergonomic 2.4GHz wireless mouse.", "19.99"),
    ("Mechanical Keyboard", "RGB mechanical keyboard.", "79.99"),
    ("USB-C Hub", "7-in-1 USB-C hub.", "34.50"),
    ("Noise-Cancelling Headphones", "Bluetooth ANC headphones.", "129.00"),
    ("4K Monitor", "27-inch 4K IPS monitor.", "299.99"),
]


def seed_catalog(users):
    Product.objects.all().delete()
    Collection.objects.all().delete()
    Brand.objects.all().delete()

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

    return brands, collections, PRODUCTS
