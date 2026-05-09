from django.urls import path

from .views import (
    BootstrapModulesView,
    ModuleDetailView,
    ModuleListCreateView,
    MyPermissionsView,
    RoleModulePermissionDetailView,
    RoleModulePermissionListCreateView,
)

app_name = "rbac"

urlpatterns = [
    path("modules/", ModuleListCreateView.as_view(), name="modules"),
    path("modules/<int:pk>/", ModuleDetailView.as_view(), name="module-detail"),
    path("permissions/", RoleModulePermissionListCreateView.as_view(), name="permissions"),
    path("permissions/<int:pk>/", RoleModulePermissionDetailView.as_view(), name="permission-detail"),
    path("me/", MyPermissionsView.as_view(), name="my-permissions"),
    path("bootstrap/", BootstrapModulesView.as_view(), name="bootstrap"),
]
