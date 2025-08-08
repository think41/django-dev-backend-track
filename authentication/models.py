from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from user.models import User
import logging

logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def register_user(user_data):
        """
        Creates new user account with validation and role assignment
        """
        try:
            # Validate password
            validate_password(user_data['password'])
            
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                role=user_data.get('role', 'user')
            )
            
            return user
        except ValidationError as e:
            raise ValidationError(f"Password validation failed: {e}")
        except IntegrityError as e:
            raise IntegrityError(f"User creation failed: {e}")
    
    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticates user and generates JWT
        """
        user = authenticate(username=username, password=password)
        if user is None:
            logger.warning(f"Failed login attempt for username: {username}")
            return None
        return user
    
    @staticmethod
    def generate_jwt_tokens(user):
        """
        Creates access and refresh tokens with user claims including role
        """
        refresh = RefreshToken()
        refresh['user_id'] = user.id
        refresh['role'] = user.role
        
        access_token = refresh.access_token
        access_token['user_id'] = user.id
        access_token['role'] = user.role
        
        return {
            'access': str(access_token),
            'refresh': str(refresh)
        }
    
    @staticmethod
    def validate_jwt_token(token):
        """
        Validates JWT token and extracts user info
        """
        try:
            refresh = RefreshToken(token)
            user_id = refresh['user_id']
            role = refresh['role']
            return {'user_id': user_id, 'role': role}
        except (InvalidToken, TokenError) as e:
            logger.error(f"Token validation failed: {e}")
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """
        Generates new access token
        """
        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            access_token['user_id'] = refresh['user_id']
            access_token['role'] = refresh['role']
            return str(access_token)
        except (InvalidToken, TokenError) as e:
            logger.error(f"Token refresh failed: {e}")
            return None
    
    @staticmethod
    def logout_user(refresh_token):
        """
        Invalidates refresh token for logout
        """
        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
            return True
        except (InvalidToken, TokenError) as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    @staticmethod
    def verify_token(token):
        """
        Verifies token validity and returns user info
        Handles both access and refresh tokens
        """
        try:
            # Try to decode as access token first
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                role = access_token['role']
            except (InvalidToken, TokenError):
                # If access token fails, try as refresh token
                refresh_token = RefreshToken(token)
                user_id = refresh_token['user_id']
                role = refresh_token['role']
            
            user = User.objects.get(id=user_id)
            return {
                'valid': True,
                'user_id': user_id,
                'role': role,
                'username': user.username,
                'email': user.email
            }
        except (InvalidToken, TokenError, User.DoesNotExist) as e:
            logger.error(f"Token verification failed: {e}")
            return {'valid': False}
