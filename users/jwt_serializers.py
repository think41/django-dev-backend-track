from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that adds user_id and role claims to the token payload.
    """
    @classmethod
    def get_token(cls, user):
        """
        Add custom claims to the token payload.
        
        Args:
            user: The user for whom the token is being generated
            
        Returns:
            Token: The JWT token with custom claims
        """
        token = super().get_token(user)
        
        # Add custom claims
        token['user_id'] = user.id
        token['role'] = user.role
        
        # Note: 'exp' (expiration) claim is already included by default in the JWT token
        
        return token
