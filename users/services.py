from django.contrib.auth.hashers import make_password
from .models import User


class UserRegistrationService:
    @staticmethod
    def create_user(username, password, email):
        """
        Creates a new user account with hashed password, default role as member,
        and is_active set to False requiring admin approval.
        """
        user = User.objects.create(
            username=username,
            password=make_password(password),
            email=email,
            role='member',
            is_active=False
        )
        return user


class UserActivationService:
    @staticmethod
    def activate_user(user_id):
        """
        Finds a user by ID and sets their is_active status to True.
        """
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return user
        except User.DoesNotExist:
            return None