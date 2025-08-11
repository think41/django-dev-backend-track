from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'email': {'required': True}
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=False,  # User starts as inactive, requiring admin approval
            role='member'     # Default role is 'member'
        )
        return user


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_active')
        read_only_fields = fields
