from typing import Tuple
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserService:
    @staticmethod
    def register(username: str, email: str, password: str, role: str = "MEMBER") -> User:
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            raise ValueError("User with provided username or email already exists.")
        user = User(
            username=username,
            email=email,
            password=make_password(password),
            role=role,
            is_active=False,
        )
        user.save()
        return user

    @staticmethod
    def approve_user(user: User) -> User:
        user.is_active = True
        user.save(update_fields=["is_active", "updated_at"])  # updated_at via auto_now
        return user

    @staticmethod
    def update_role(user: User, role: str) -> User:
        user.role = role
        user.save(update_fields=["role", "updated_at"])  # updated_at via auto_now
        return user

    @staticmethod
    def create_tokens_for_user(user: User) -> Tuple[str, str]:
        refresh = RefreshToken.for_user(user)
        return str(refresh), str(refresh.access_token)
