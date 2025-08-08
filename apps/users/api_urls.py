from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import AuthViewSet, MembersViewSet, PublicUsersViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'members', MembersViewSet, basename='members')
router.register(r'public/users', PublicUsersViewSet, basename='public-users')

urlpatterns = [
    path('', include(router.urls)),
]
