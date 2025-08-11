from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationService:
    """
    Service for handling user registration logic.
    """
    @staticmethod
    def create_user(username, password, email):
        """
        Creates a new user account with default role 'member' and inactive status.
        
        Args:
            username (str): The username for the new user
            password (str): The password for the new user
            email (str): The email address for the new user
            
        Returns:
            User: The newly created user instance
        """
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            role='member',
            is_active=False
        )
        return user


class UserActivationService:
    """
    Service for handling user activation logic.
    """
    @staticmethod
    def activate_user(user_id):
        """
        Activates a user account by setting is_active to True.
        
        Args:
            user_id (int): The ID of the user to activate
            
        Returns:
            User: The activated user instance
            
        Raises:
            User.DoesNotExist: If no user with the given ID exists
        """
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save(update_fields=['is_active'])
        return user
