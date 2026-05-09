from django.db import models

from ecommerce.common.models import TimeStampedModel
from ecommerce.users.models import Role


class Module(TimeStampedModel):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class RoleModulePermission(TimeStampedModel):
    role = models.CharField(max_length=20, choices=Role.choices)
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="role_permissions"
    )
    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["role", "module"], name="uq_role_module_permission"
            )
        ]
        ordering = ("role", "module__name")

    def __str__(self):
        return f"{self.role} -> {self.module.code}"

    def can(self, action: str) -> bool:
        return bool(getattr(self, f"can_{action}", False))
