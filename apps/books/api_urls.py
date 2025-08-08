from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import BookViewSet, BorrowViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'borrow', BorrowViewSet, basename='borrow')

urlpatterns = [
    path('', include(router.urls)),
]
