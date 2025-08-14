from django.urls import path
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.register, name='user-register'),
    path('login/', views.login, name='user-login'),
    
    # Admin endpoints
    path('admin/users/', views.list_users, name='admin-list-users'),
    path('admin/users/<int:user_id>/approve/', views.approve_user, name='admin-approve-user'),
] 