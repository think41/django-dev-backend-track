from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from .jwt_custom import CustomTokenObtainPairView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.logout, name='logout')
]