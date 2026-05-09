from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView

from ecommerce.common.permissions import IsAdminOrSuperAdmin, IsSuperAdmin
from ecommerce.common.responses import APIResponse

from .models import AdminProfile, CustomerProfile, Role, User, VendorProfile
from .serializers import (
    AdminProfileSerializer,
    AdminUserManagementSerializer,
    ChangePasswordSerializer,
    CustomerProfileSerializer,
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    UpdateUserSerializer,
    UserSerializer,
    VendorProfileSerializer,
)
from .services import UserService


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = UserService.create_user(serializer.validated_data)
        tokens = UserService.issue_tokens(user)
        return APIResponse.created(
            {"user": UserSerializer(user).data, "tokens": tokens},
            message="Registered successfully.",
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = UserService.issue_tokens(user)
        return APIResponse.success(
            {"user": UserSerializer(user).data, "tokens": tokens},
            message="Logged in successfully.",
        )


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.no_content(message="Logged out.")


class MeView(generics.RetrieveUpdateAPIView):
    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UpdateUserSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = UpdateUserSerializer(
            instance=request.user, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = UserService.update_user(request.user, serializer.validated_data)
        return APIResponse.success(
            UserSerializer(user).data, message="Profile updated."
        )

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        UserService.change_password(
            request.user,
            serializer.validated_data["old_password"],
            serializer.validated_data["new_password"],
        )
        return APIResponse.success(message="Password changed.")


class _OwnedProfileView(generics.RetrieveUpdateAPIView):
    profile_attr = ""
    profile_model = None
    serializer_class = None

    def get_object(self):
        return get_object_or_404(self.profile_model, user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        return APIResponse.success(
            self.serializer_class(self.get_object()).data,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.serializer_class(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse.success(serializer.data, message="Profile updated.")


class CustomerProfileView(_OwnedProfileView):
    profile_model = CustomerProfile
    serializer_class = CustomerProfileSerializer

    def get_object(self):
        if self.request.user.role != Role.CUSTOMER:
            self.permission_denied(self.request, message="Customer role required.")
        return super().get_object()


class VendorProfileView(_OwnedProfileView):
    profile_model = VendorProfile
    serializer_class = VendorProfileSerializer

    def get_object(self):
        if self.request.user.role != Role.VENDOR:
            self.permission_denied(self.request, message="Vendor role required.")
        return super().get_object()


class AdminProfileView(_OwnedProfileView):
    permission_classes = [IsAdminOrSuperAdmin]
    profile_model = AdminProfile
    serializer_class = AdminProfileSerializer


class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = User.objects.all()
    serializer_class = AdminUserManagementSerializer
    filterset_fields = ["role", "is_active", "is_email_verified"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering_fields = ["date_joined", "email"]


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSuperAdmin]
    queryset = User.objects.all()
    serializer_class = AdminUserManagementSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return APIResponse.error(
                "You cannot delete your own account.",
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        user.save(update_fields=["is_active"])
        return APIResponse.no_content(message="User deactivated.")
