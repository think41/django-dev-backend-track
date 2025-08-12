from django.contrib.auth import get_user_model
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserRegistrationSerializer, UserListSerializer
from .services import UserRegistrationService, UserActivationService
from .permissions import IsAdmin

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Creates a new user with inactive status, pending admin approval.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Registration successful. Your account is pending approval from an administrator."},
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class UserLoginView(TokenObtainPairView):
    """
    API endpoint for user login.
    Uses JWT token authentication with custom claims (user_id, role, exp).
    """
    from .jwt_serializers import CustomTokenObtainPairSerializer
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = (AllowAny,)


class UserListView(generics.ListAPIView):
    """
    API endpoint for listing users.
    Only accessible by admin users.
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAdmin,)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['username', 'email', 'date_joined']
    
    def get_queryset(self):
        queryset = User.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
        return queryset


class UserApprovalView(APIView):
    """
    API endpoint for approving user registrations.
    Only accessible by admin users.
    """
    permission_classes = (IsAdmin,)
    
    def patch(self, request, id):
        try:
            user = UserActivationService.activate_user(id)
            return Response({"message": "User account activated successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
