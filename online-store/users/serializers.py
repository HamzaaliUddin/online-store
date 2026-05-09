from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AdminProfile, CustomerProfile, Role, User, VendorProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "is_email_verified",
            "is_phone_verified",
            "is_active",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "is_email_verified",
            "is_phone_verified",
            "is_active",
            "date_joined",
        )


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, min_length=8, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    role = serializers.ChoiceField(
        choices=[(Role.CUSTOMER, "Customer"), (Role.VENDOR, "Vendor")],
        default=Role.CUSTOMER,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "password",
            "confirm_password",
        )

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        validate_password(attrs["password"])
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs["email"].lower(),
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs):
        try:
            RefreshToken(self.validated_data["refresh"]).blacklist()
        except Exception:
            raise serializers.ValidationError({"refresh": "Invalid or expired token."})


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = (
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "date_of_birth",
            "avatar",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = (
            "business_name",
            "business_email",
            "business_phone",
            "tax_number",
            "is_approved",
            "logo",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("is_approved", "created_at", "updated_at")


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = (
            "department",
            "designation",
            "employee_code",
            "can_access_dashboard",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("can_access_dashboard", "created_at", "updated_at")


class AdminUserManagementSerializer(serializers.ModelSerializer):
    """Used by superadmins/admins to manage users (role, active flag)."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "is_active",
            "is_email_verified",
            "is_phone_verified",
            "date_joined",
        )
        read_only_fields = ("id", "email", "date_joined")
