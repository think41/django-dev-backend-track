from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import BookViewSet, BorrowViewSet, FineViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'borrow', BorrowViewSet, basename='borrow')
router.register(r'fines', FineViewSet, basename='fine')

urlpatterns = [
    path('', include(router.urls)),
]
