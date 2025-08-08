from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    # Use is_active as approval flag. Default from AbstractUser is True, override to False.
    is_active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"

