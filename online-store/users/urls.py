from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AdminProfileView,
    AdminUserDetailView,
    AdminUserListView,
    ChangePasswordView,
    CustomerProfileView,
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    VendorProfileView,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("me/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("me/customer-profile/", CustomerProfileView.as_view(), name="customer-profile"),
    path("me/vendor-profile/", VendorProfileView.as_view(), name="vendor-profile"),
    path("me/admin-profile/", AdminProfileView.as_view(), name="admin-profile"),
    path("admin/users/", AdminUserListView.as_view(), name="admin-users"),
    path("admin/users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
]
