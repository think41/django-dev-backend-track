from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegistrationView,
    UserLoginView,
    UserListView,
    UserApprovalView,
)

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Admin endpoints
    path('admin/users/', UserListView.as_view(), name='admin-user-list'),
    path('admin/users/<int:id>/approve/', UserApprovalView.as_view(), name='admin-user-approve'),
]
