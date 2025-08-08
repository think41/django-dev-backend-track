from django.contrib.auth import authenticate, get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from ..services import UserService
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, TokenResponseSerializer

User = get_user_model()


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", "") == "ADMIN")


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer  # default for schema generation

    @extend_schema(request=RegisterSerializer, responses={201: TokenResponseSerializer})
    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = UserService.register(data["username"], data["email"], data["password"], data.get("role", "MEMBER"))
        refresh, access = UserService.create_tokens_for_user(user)
        return Response({
            "message": "User registered. Awaiting admin approval.",
            "is_active": user.is_active,
            "refresh": refresh,
            "access": access,
        }, status=status.HTTP_201_CREATED)

    @extend_schema(request=LoginSerializer, responses={200: TokenResponseSerializer})
    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data["identifier"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=identifier, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if not user:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

        refresh, access = UserService.create_tokens_for_user(user)
        return Response({
            "message": "Login successful" if user.is_active else "User not active",
            "is_active": user.is_active,
            "refresh": refresh,
            "access": access,
            "role": user.role,
        })


class MembersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["update_roles", "approve_user", "list", "retrieve", "borrow_history", "borrow_history_for_book"]:
            return [IsAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], url_path="approve-user")
    def approve_user(self, request, pk=None):
        user = self.get_object()
        UserService.approve_user(user)
        return Response({"message": "User approved"})

    @action(detail=True, methods=["post"], url_path="update-roles")
    def update_roles(self, request, pk=None):
        role = request.data.get("role")
        if role not in ("ADMIN", "MEMBER"):
            return Response({"detail": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)
        user = self.get_object()
        UserService.update_role(user, role)
        return Response({"message": "Role updated", "role": user.role})

    @extend_schema(operation_id="members_borrow_list")
    @action(detail=True, methods=["get"], url_path="borrow")
    def borrow_history(self, request, pk=None):
        from apps.books.models import BorrowRecord
        records = BorrowRecord.objects.filter(user_id=pk).order_by("-created_at")
        data = [
            {
                "id": str(r.id),
                "book_id": str(r.book_id),
                "status": r.status,
                "borrow_date": r.borrow_date,
                "return_date": r.return_date,
            }
            for r in records
        ]
        return Response(data)
    
    @extend_schema(operation_id="members_borrow_for_book", parameters=[
        OpenApiParameter(name="book_id", type=OpenApiTypes.STR, location=OpenApiParameter.PATH)
    ])
    @action(detail=True, methods=["get"], url_path="borrow/(?P<book_id>[^/.]+)")
    def borrow_history_for_book(self, request, pk=None, book_id=None):
        from apps.books.models import BorrowRecord
        records = BorrowRecord.objects.filter(user_id=pk, book_id=book_id).order_by("-created_at")
        data = [
            {
                "id": str(r.id),
                "book_id": str(r.book_id),
                "status": r.status,
                "borrow_date": r.borrow_date,
                "return_date": r.return_date,
            }
            for r in records
        ]
        return Response(data)


class PublicUsersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(operation_id="public_users_list")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
