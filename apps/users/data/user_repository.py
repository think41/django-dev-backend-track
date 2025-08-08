from typing import Optional
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserRepository:
    @staticmethod
    def get_by_id(user_id) -> Optional[User]:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_by_username_or_email(identifier: str) -> Optional[User]:
        try:
            return User.objects.get(models.Q(username=identifier) | models.Q(email=identifier))
        except User.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return User.objects.all().order_by("-date_joined")
