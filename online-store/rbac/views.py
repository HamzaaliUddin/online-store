from rest_framework import generics
from rest_framework.views import APIView

from ecommerce.common.permissions import IsAdminOrSuperAdmin, IsSuperAdmin
from ecommerce.common.responses import APIResponse

from .models import Module, RoleModulePermission
from .serializers import ModuleSerializer, RoleModulePermissionSerializer
from .services import RBACService


class ModuleListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    search_fields = ["code", "name", "description"]
    filterset_fields = ["is_active"]
    ordering_fields = ["name", "code", "created_at"]

    def get_permissions(self):
        if self.request.method != "GET":
            return [IsSuperAdmin()]
        return super().get_permissions()


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperAdmin]
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer


class RoleModulePermissionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsSuperAdmin]
    queryset = RoleModulePermission.objects.select_related("module").all()
    serializer_class = RoleModulePermissionSerializer
    filterset_fields = ["role", "module"]
    search_fields = ["module__code", "module__name"]
    ordering_fields = ["role", "module__name", "created_at"]


class RoleModulePermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperAdmin]
    queryset = RoleModulePermission.objects.select_related("module").all()
    serializer_class = RoleModulePermissionSerializer


class MyPermissionsView(APIView):
    """Returns the current user's effective module permissions."""

    def get(self, request):
        role = request.user.role
        if role == "superadmin" or request.user.is_superuser:
            modules = Module.objects.filter(is_active=True)
            data = [
                {
                    "module": m.code,
                    "name": m.name,
                    "can_view": True,
                    "can_create": True,
                    "can_update": True,
                    "can_delete": True,
                }
                for m in modules
            ]
        else:
            qs = RoleModulePermission.objects.select_related("module").filter(
                role=role, module__is_active=True
            )
            data = [
                {
                    "module": p.module.code,
                    "name": p.module.name,
                    "can_view": p.can_view,
                    "can_create": p.can_create,
                    "can_update": p.can_update,
                    "can_delete": p.can_delete,
                }
                for p in qs
            ]
        return APIResponse.success({"role": role, "permissions": data})


class BootstrapModulesView(APIView):
    permission_classes = [IsSuperAdmin]

    def post(self, request):
        RBACService.bootstrap_default_modules_and_permissions()
        return APIResponse.success(message="Default modules and permissions seeded.")
