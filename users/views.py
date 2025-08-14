from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q

from .models import User
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .services import UserRegistrationService, UserActivationService
from .permissions import IsAdminUser


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Allows a new user to register for an account. 
    The account is created as inactive and requires admin approval.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        try:
            user = UserRegistrationService.create_user(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
                email=serializer.validated_data['email']
            )
            return Response(
                {"message": "Registration successful. Your account is pending approval from an administrator."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Authenticates an active user and provides JWT access and refresh tokens.
    """
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_users(request):
    """
    Retrieves a list of all users in the system. Can be filtered by active status.
    """
    is_active = request.query_params.get('is_active', None)
    users = User.objects.all()
    
    if is_active is not None:
        is_active_bool = is_active.lower() == 'true'
        users = users.filter(is_active=is_active_bool)
    
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def approve_user(request, user_id):
    """
    Approves a user's registration by activating their account.
    """
    try:
        user = UserActivationService.activate_user(user_id)
        return Response(
            {"message": "User account activated successfully."},
            status=status.HTTP_200_OK
        )
    except ValueError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        ) 