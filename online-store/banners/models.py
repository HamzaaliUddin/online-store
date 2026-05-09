from django.db import models
from django.utils import timezone

from ecommerce.common.models import TimeStampedModel


class Banner(TimeStampedModel):
    class Placement(models.TextChoices):
        HOME_HERO = "home_hero", "Home Hero"
        HOME_SECONDARY = "home_secondary", "Home Secondary"
        CATEGORY = "category", "Category"
        CHECKOUT = "checkout", "Checkout"

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to="banners/")
    link_url = models.URLField(blank=True)
    placement = models.CharField(
        max_length=30, choices=Placement.choices, default=Placement.HOME_HERO
    )
    position = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("placement", "position", "-created_at")
        indexes = [
            models.Index(fields=["placement", "is_active"]),
        ]

    def __str__(self):
        return f"{self.placement}: {self.title}"

    def is_live(self) -> bool:
        if not self.is_active:
            return False
        now = timezone.now()
        if self.starts_at and self.starts_at > now:
            return False
        if self.ends_at and self.ends_at < now:
            return False
        return True
