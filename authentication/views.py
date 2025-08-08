from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import AuthService
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    TokenRefreshSerializer,
    TokenVerifySerializer,
    UserResponseSerializer
)

@extend_schema(
    tags=['auth'],
    summary="User Registration",
    description="Register a new user account with validation and role assignment",
    request=UserRegistrationSerializer,
    responses={
        201: UserResponseSerializer,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Successful Registration',
            value={
                'message': 'User registered successfully',
                'user': {
                    'id': 1,
                    'username': 'john_doe',
                    'email': 'john@example.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'role': 'user'
                }
            },
            response_only=True,
            status_codes=['201']
        ),
        OpenApiExample(
            'Validation Error',
            value={
                'error': 'Password validation failed: This password is too short. It must contain at least 8 characters.'
            },
            response_only=True,
            status_codes=['400']
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    User registration endpoint
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = AuthService.register_user(serializer.validated_data)
            user_serializer = UserResponseSerializer(user)
            return Response({
                'message': 'User registered successfully',
                'user': user_serializer.data
            }, status=status.HTTP_201_CREATED)
        except (ValidationError, IntegrityError) as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['auth'],
    summary="User Login",
    description="Authenticate user and generate JWT tokens",
    request=UserLoginSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Successful Login',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
                'user': {
                    'id': 1,
                    'username': 'john_doe',
                    'email': 'john@example.com',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'role': 'user'
                }
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Invalid Credentials',
            value={
                'error': 'Invalid credentials'
            },
            response_only=True,
            status_codes=['401']
        )
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    User login endpoint
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = AuthService.authenticate_user(username, password)
        if user:
            tokens = AuthService.generate_jwt_tokens(user)
            user_serializer = UserResponseSerializer(user)
            return Response({
                'access': tokens['access'],
                'refresh': tokens['refresh'],
                'user': user_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['auth'],
    summary="Refresh Token",
    description="Refresh JWT access token using refresh token",
    request=TokenRefreshSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Successful Refresh',
            value={
                'access': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Invalid Refresh Token',
            value={
                'error': 'Invalid refresh token'
            },
            response_only=True,
            status_codes=['401']
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    """
    Refresh JWT access token endpoint
    """
    serializer = TokenRefreshSerializer(data=request.data)
    if serializer.is_valid():
        refresh_token = serializer.validated_data['refresh']
        new_access_token = AuthService.refresh_access_token(refresh_token)
        
        if new_access_token:
            return Response({
                'access': new_access_token
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['auth'],
    summary="User Logout",
    description="Logout user by invalidating refresh token",
    request=TokenRefreshSerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Successful Logout',
            value={
                'message': 'Logged out successfully'
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Invalid Refresh Token',
            value={
                'error': 'Invalid refresh token'
            },
            response_only=True,
            status_codes=['400']
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    User logout endpoint
    """
    serializer = TokenRefreshSerializer(data=request.data)
    if serializer.is_valid():
        refresh_token = serializer.validated_data['refresh']
        success = AuthService.logout_user(refresh_token)
        
        if success:
            return Response({
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=['auth'],
    summary="Verify Token",
    description="Verify JWT token validity and return user information",
    request=TokenVerifySerializer,
    responses={
        200: OpenApiTypes.OBJECT,
        401: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Valid Token',
            value={
                'valid': True,
                'user_info': {
                    'user_id': 1,
                    'role': 'user',
                    'username': 'john_doe',
                    'email': 'john@example.com'
                }
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Invalid Token',
            value={
                'valid': False,
                'error': 'Invalid token'
            },
            response_only=True,
            status_codes=['401']
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Verify JWT token validity endpoint
    """
    serializer = TokenVerifySerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        token_info = AuthService.verify_token(token)
        
        if token_info['valid']:
            return Response({
                'valid': True,
                'user_info': {
                    'user_id': token_info['user_id'],
                    'role': token_info['role'],
                    'username': token_info['username'],
                    'email': token_info['email']
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'valid': False,
                'error': 'Invalid token'
            }, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
