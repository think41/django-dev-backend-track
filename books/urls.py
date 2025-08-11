from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    BorrowRequestView,
    BookReturnView,
    AdminBorrowListView,
    AdminBorrowApprovalView,
    AdminBorrowRejectionView,
)

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'', BookViewSet)

urlpatterns = [
    # Book catalog endpoints
    path('', include(router.urls)),
    
    # Borrowing endpoints
    path('borrow/', BorrowRequestView.as_view(), name='borrow-request'),
    path('return/', BookReturnView.as_view(), name='book-return'),
    
    # Admin borrowing endpoints
    path('admin/borrow/', AdminBorrowListView.as_view(), name='admin-borrow-list'),
    path('admin/borrow/<int:id>/approve/', AdminBorrowApprovalView.as_view(), name='admin-borrow-approve'),
    path('admin/borrow/<int:id>/reject/', AdminBorrowRejectionView.as_view(), name='admin-borrow-reject'),
]
