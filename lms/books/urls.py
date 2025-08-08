"""
URL configuration for the Books app.

This module defines all URL patterns for book-related API endpoints
as specified in the books spec.md file.
"""

from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Public Book Endpoints
    path('search/', views.BookSearchView.as_view(), name='book-search'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    
    # Admin Book Management Endpoints
    path('admin/', views.admin_book_list_create, name='admin-book-list-create'),
    path('admin/<int:pk>/', views.admin_book_detail, name='admin-book-detail'),
    
    # Alternative class-based view URLs (if preferred)
    # path('admin/', views.AdminBookListView.as_view(), name='admin-book-list'),
    # path('admin/create/', views.AdminBookCreateView.as_view(), name='admin-book-create'),
    # path('admin/<int:pk>/update/', views.AdminBookUpdateView.as_view(), name='admin-book-update'),
    # path('admin/<int:pk>/delete/', views.AdminBookDeleteView.as_view(), name='admin-book-delete'),
]