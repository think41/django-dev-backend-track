"""
Views for the Authentication app.

This module contains all API views for authentication operations,
including registration, login, and token management.
"""

from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserInfoSerializer
)

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    POST /api/auth/register/
    
    Creates new users with PENDING status requiring admin approval.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create new user and return success message."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        return Response({
            'message': 'Registration successful! Your account is pending approval.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'status': user.status
            }
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with user information.
    POST /api/auth/login/
    
    Authenticates users and returns JWT tokens with user info.
    Only allows login for ACTIVE users.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        """Handle login request with custom response format."""
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Add success message to response
                response.data['message'] = 'Login successful'
                
            return response
            
        except Exception as e:
            # Handle any authentication errors
            return Response({
                'error': 'Authentication failed',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view.
    POST /api/auth/refresh/
    
    Refreshes access tokens using refresh tokens.
    """
    
    def post(self, request, *args, **kwargs):
        """Handle token refresh with custom response format."""
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                # Add success message to response
                response.data['message'] = 'Token refreshed successfully'
                
            return response
            
        except Exception as e:
            return Response({
                'error': 'Token refresh failed',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_logout(request):
    """
    API endpoint for user logout.
    POST /api/auth/logout/
    
    Blacklists the refresh token to prevent further use.
    """
    try:
        refresh_token = request.data.get('refresh_token')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Logout failed',
            'detail': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_profile_info(request):
    """
    API endpoint to get current user profile information.
    GET /api/auth/profile/
    
    Returns current user information based on JWT token.
    """
    if not request.user.is_authenticated:
        return Response({
            'error': 'Authentication required'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    serializer = UserInfoSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_status(request):
    """
    API endpoint to check authentication status.
    GET /api/auth/status/
    
    Returns information about the current authentication state.
    """
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'user': UserInfoSerializer(request.user).data
        })
    else:
        return Response({
            'authenticated': False,
            'user': None
        })


# Function-based alternative views
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Alternative function-based registration view.
    POST /api/auth/register/
    """
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'message': 'Registration successful! Your account is pending approval.',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'status': user.status
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Alternative function-based login view.
    POST /api/auth/login/
    """
    serializer = CustomTokenObtainPairSerializer(data=request.data)
    
    if serializer.is_valid():
        return Response({
            'message': 'Login successful',
            **serializer.validated_data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Login failed',
        'details': serializer.errors
    }, status=status.HTTP_401_UNAUTHORIZED)


# Health check endpoint for authentication service
@api_view(['GET'])
@permission_classes([AllowAny])
def auth_health_check(request):
    """
    Health check endpoint for the authentication service.
    GET /api/auth/health/
    """
    return Response({
        'status': 'healthy',
        'service': 'authentication',
        'message': 'Authentication service is running properly'
    }, status=status.HTTP_200_OK)