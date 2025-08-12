from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BookViewSet,
    BorrowRequestView,
    BookReturnView,
    AdminBorrowListView,
    AdminBorrowApprovalView,
    AdminBorrowRejectionView,
    ReservationCreateView,
    ReservationCancelView,
    UserReservationListView,
    AdminReservationListView,
    UserFineListView,
    AdminFineListView,
    AdminFinePaymentView,
    AdminFineWaiverView,
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
    
    # Reservation endpoints
    path('reserve/', ReservationCreateView.as_view(), name='reservation-create'),
    path('reserve/cancel/', ReservationCancelView.as_view(), name='reservation-cancel'),
    path('reservations/', UserReservationListView.as_view(), name='user-reservation-list'),
    path('admin/reservations/', AdminReservationListView.as_view(), name='admin-reservation-list'),
    
    # Fine endpoints
    path('fines/', UserFineListView.as_view(), name='user-fine-list'),
    path('admin/fines/', AdminFineListView.as_view(), name='admin-fine-list'),
    path('admin/fines/<int:id>/pay/', AdminFinePaymentView.as_view(), name='admin-fine-pay'),
    path('admin/fines/<int:id>/waive/', AdminFineWaiverView.as_view(), name='admin-fine-waive'),
]
