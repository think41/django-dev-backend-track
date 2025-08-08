from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer, TokenResponseSerializer, MessageResponseSerializer
from .services import UserRegistrationService, UserActivationService


@swagger_auto_schema(
    method='post',
    request_body=UserRegistrationSerializer,
    responses={
        201: MessageResponseSerializer,
        400: 'Bad Request - Invalid data'
    },
    operation_description='Register a new user account. Account will be created as inactive pending admin approval.',
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """
    POST /api/users/register/
    Allows a new user to register for an account.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        email = serializer.validated_data['email']
        
        # Use the service to create user
        user = UserRegistrationService.create_user(username, password, email)
        
        return Response(
            {"message": "Registration successful. Your account is pending approval from an administrator."},
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=UserLoginSerializer,
    responses={
        200: TokenResponseSerializer,
        401: 'Unauthorized - Invalid credentials or inactive account'
    },
    operation_description='Authenticate a user and receive JWT tokens. Only active users can login.',
    tags=['Authentication']
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """
    POST /api/users/login/
    Authenticates an active user and provides JWT access and refresh tokens.
    """
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims to JWT payload
        refresh['user_id'] = user.id
        refresh['role'] = user.role
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('is_active', openapi.IN_QUERY, description='Filter by active status (true/false)', type=openapi.TYPE_BOOLEAN),
    ],
    responses={
        200: UserSerializer(many=True),
        403: 'Forbidden - Admin access required'
    },
    operation_description='Retrieve a list of all users. Admin only. Can filter by active status.',
    tags=['Admin - User Management']
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_users(request):
    """
    GET /api/admin/users/
    Retrieves a list of all users in the system. Admin only.
    """
    # Check if user is admin
    if request.user.role != 'admin':
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Filter by is_active if provided
    is_active = request.query_params.get('is_active')
    users = User.objects.all()
    
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        users = users.filter(is_active=is_active_bool)
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='patch',
    responses={
        200: MessageResponseSerializer,
        403: 'Forbidden - Admin access required',
        404: 'Not Found - User does not exist'
    },
    operation_description='Approve a user registration by activating their account. Admin only.',
    tags=['Admin - User Management']
)
@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def approve_user(request, user_id):
    """
    PATCH /api/admin/users/{id}/approve/
    Approves a user's registration by activating their account. Admin only.
    """
    # Check if user is admin
    if request.user.role != 'admin':
        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Use the service to activate user
    user = UserActivationService.activate_user(user_id)
    
    if user:
        return Response(
            {"message": "User account activated successfully."},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"detail": "User not found."},
            status=status.HTTP_404_NOT_FOUND
        )
