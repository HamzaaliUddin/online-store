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


def seed_users():
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

    return users
