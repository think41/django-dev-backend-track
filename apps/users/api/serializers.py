from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[("ADMIN", "ADMIN"), ("MEMBER", "MEMBER")], default="MEMBER")


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(help_text="username or email")
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "is_active", "date_joined", "last_login")


class TokenResponseSerializer(serializers.Serializer):
    message = serializers.CharField(required=False)
    is_active = serializers.BooleanField()
    refresh = serializers.CharField()
    access = serializers.CharField()
    role = serializers.ChoiceField(choices=[("ADMIN", "ADMIN"), ("MEMBER", "MEMBER")], required=False)
