from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('refresh/', views.refresh_token, name='refresh'),
    path('logout/', views.logout_user, name='logout'),
    path('verify/', views.verify_token, name='verify'),
] 