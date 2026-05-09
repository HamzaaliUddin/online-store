from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(validated_data: dict) -> User:
        validated_data.pop("confirm_password", None)
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)

    @staticmethod
    def issue_tokens(user: User) -> dict:
        refresh = RefreshToken.for_user(user)
        refresh["role"] = user.role
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

    @staticmethod
    @transaction.atomic
    def update_user(user: User, validated_data: dict) -> User:
        for field, value in validated_data.items():
            setattr(user, field, value)
        user.full_clean()
        user.save()
        return user

    @staticmethod
    @transaction.atomic
    def change_password(user: User, old_password: str, new_password: str) -> None:
        if not user.check_password(old_password):
            raise ValidationError({"old_password": "Old password is incorrect."})
        if old_password == new_password:
            raise ValidationError(
                {"new_password": "New password must differ from the old one."}
            )
        user.set_password(new_password)
        user.save(update_fields=["password"])
