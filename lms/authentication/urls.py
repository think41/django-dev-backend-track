"""
URL configuration for the Authentication app.

This module defines all URL patterns for authentication-related API endpoints
as specified in the authentication spec.md file.
"""

from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # User Registration
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # JWT Authentication
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh/', views.CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', views.user_logout, name='logout'),
    
    # User Info
    path('profile/', views.user_profile_info, name='profile-info'),
    path('status/', views.auth_status, name='auth-status'),
    
    # Health Check
    path('health/', views.auth_health_check, name='health-check'),
    
    # Alternative function-based endpoints (if needed)
    # path('register-alt/', views.register_user, name='register-alt'),
    # path('login-alt/', views.login_user, name='login-alt'),
]