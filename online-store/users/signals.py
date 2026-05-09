from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AdminProfile, CustomerProfile, Role, User, VendorProfile


@receiver(post_save, sender=User)
def create_role_profile(sender, instance: User, created, **kwargs):
    if not created:
        return
    if instance.role == Role.CUSTOMER:
        CustomerProfile.objects.get_or_create(user=instance)
    elif instance.role == Role.VENDOR:
        VendorProfile.objects.get_or_create(
            user=instance,
            defaults={"business_name": instance.full_name or instance.email},
        )
    elif instance.role in (Role.ADMIN, Role.SUPERADMIN):
        AdminProfile.objects.get_or_create(user=instance)
