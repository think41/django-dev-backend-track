from django.urls import path
from . import views

urlpatterns = [
    # User Registration and Login
    path('register/', views.register_user, name='register_user'),
    path('login/', views.login_user, name='login_user'),
    
    # Admin User Management
    path('list/', views.list_users, name='list_users'),
    path('<int:user_id>/approve/', views.approve_user, name='approve_user'),
]