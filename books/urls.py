from django.urls import path

from .views import (
    AdminApproveBorrowView,
    AdminBorrowListView,
    AdminRejectBorrowView,
    BookListCreateView,
    BookRetrieveUpdateDestroyView,
    BorrowRequestView,
    ReturnBookView,
)

urlpatterns = [
    path("", BookListCreateView.as_view(), name="books-list-create"),
    path("<int:pk>/", BookRetrieveUpdateDestroyView.as_view(), name="books-rud"),
    path("borrow/", BorrowRequestView.as_view(), name="books-borrow"),
    path("return/", ReturnBookView.as_view(), name="books-return"),
    # Admin
    path("admin/borrow/", AdminBorrowListView.as_view(), name="admin-borrow-list"),
    path("admin/borrow/<int:pk>/approve/", AdminApproveBorrowView.as_view(), name="admin-borrow-approve"),
    path("admin/borrow/<int:pk>/reject/", AdminRejectBorrowView.as_view(), name="admin-borrow-reject"),
]

