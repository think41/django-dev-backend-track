from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.user_profile, name='user_profile'),
    path('me/update/', views.update_profile, name='update_profile'),
]