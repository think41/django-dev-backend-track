from rest_framework import serializers
from user.models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        help_text="Password for the user account (minimum 8 characters)"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
            'role': {'required': False, 'help_text': 'User role: "user" or "admin" (defaults to "user")'},
            'username': {'help_text': 'Unique username for the user account'},
            'email': {'help_text': 'Valid email address for the user account'},
            'first_name': {'help_text': 'User\'s first name'},
            'last_name': {'help_text': 'User\'s last name'},
        }
    
    def validate_role(self, value):
        if value and value not in ['user', 'admin']:
            raise serializers.ValidationError("Role must be either 'user' or 'admin'")
        return value or 'user'
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        help_text="Username for authentication"
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Password for authentication"
    )

class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(
        help_text="Refresh token for generating new access token"
    )

class TokenVerifySerializer(serializers.Serializer):
    token = serializers.CharField(
        help_text="JWT token to verify"
    )

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']
        read_only_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role'] 