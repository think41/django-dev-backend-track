"""
Serializers for the Authentication app.

This module contains serializers for authentication-related endpoints,
including registration, login, and token management.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Creates new users with PENDING status requiring admin approval.
    """
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
    
    def validate_username(self, value):
        """Validate username format and uniqueness."""
        if not value.strip():
            raise serializers.ValidationError("Username cannot be empty.")
        
        # Check for existing username (case-insensitive)
        if User.objects.filter(username__iexact=value.strip()).exists():
            raise serializers.ValidationError(
                "A user with that username already exists."
            )
        
        return value.strip()
    
    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if not value.strip():
            raise serializers.ValidationError("Email cannot be empty.")
        
        # Check for existing email (case-insensitive)
        if User.objects.filter(email__iexact=value.strip()).exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        
        return value.strip().lower()
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Password confirmation doesn't match password."
            })
        return attrs
    
    def create(self, validated_data):
        """Create a new user with PENDING status."""
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm')
        
        # Create user with PENDING status
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            status='PENDING'  # All new users start as pending
        )
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user information in the response
    and validates user status.
    """
    
    def validate(self, attrs):
        """Validate credentials and user status."""
        # Use username for authentication
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError({
                'detail': 'Username and password are required.'
            })
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError({
                'detail': 'Invalid username or password.'
            })
        
        # Check if user account is active
        if user.status != 'ACTIVE':
            if user.status == 'PENDING':
                raise serializers.ValidationError({
                    'detail': 'Your account is pending approval. Please wait for admin approval.'
                })
            elif user.status == 'SUSPENDED':
                raise serializers.ValidationError({
                    'detail': 'Your account has been suspended. Please contact the administrator.'
                })
            else:
                raise serializers.ValidationError({
                    'detail': 'Your account is not active.'
                })
        
        # Get tokens using parent class method
        data = super().validate(attrs)
        
        # Add user information to the response
        data.update({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'status': user.status
            }
        })
        
        return data
    
    @classmethod
    def get_token(cls, user):
        """Customize token claims with user role and status."""
        token = super().get_token(user)
        
        # Add custom claims
        token['user_id'] = user.id
        token['role'] = user.role
        token['status'] = user.status
        
        return token


class UserInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for user information in authentication responses.
    """
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'status', 'date_joined')
        read_only_fields = ('id', 'username', 'email', 'role', 'status', 'date_joined')


class LoginSerializer(serializers.Serializer):
    """
    Alternative login serializer (if not using JWT library's built-in serializer).
    """
    
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(
        max_length=128,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate login credentials and user status."""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError(
                'Username and password are required.'
            )
        
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError(
                'Invalid username or password.'
            )
        
        if user.status != 'ACTIVE':
            if user.status == 'PENDING':
                raise serializers.ValidationError(
                    'Your account is pending approval.'
                )
            elif user.status == 'SUSPENDED':
                raise serializers.ValidationError(
                    'Your account has been suspended.'
                )
            else:
                raise serializers.ValidationError(
                    'Your account is not active.'
                )
        
        attrs['user'] = user
        return attrs