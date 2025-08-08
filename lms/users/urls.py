"""
URL configuration for the Users app.

This module defines all URL patterns for user-related API endpoints
as specified in the users spec.md file.
"""

from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User Registration
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    
    # Admin User Management Endpoints
    path('admin/', views.AdminUserListView.as_view(), name='admin-user-list'),
    path('admin/approve/<int:user_id>/', views.approve_member_registration, name='approve-member'),
    
    # Admin Borrow Management Endpoints
    path('admin/borrow-records/', views.admin_borrow_records, name='admin-borrow-records'),
    path('admin/approve-borrow/<int:user_id>/<int:book_id>/', views.approve_borrow_request, name='approve-borrow'),
    path('admin/reject-borrow/<int:user_id>/<int:book_id>/', views.reject_borrow_request, name='reject-borrow'),
    
    # User Profile Endpoints
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='user-profile-update'),
    
    # Member Borrowing Endpoints
    path('borrow/request/', views.request_borrow_book, name='borrow-request'),
    path('borrow/return/<int:book_id>/', views.return_book, name='return-book'),
    path('borrow/history/', views.borrowing_history, name='borrowing-history'),
]