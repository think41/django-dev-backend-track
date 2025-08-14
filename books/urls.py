from django.urls import path
from . import views

urlpatterns = [
    # Book endpoints
    path('', views.book_list_create, name='book-list-create'),
    path('<int:book_id>/', views.book_detail, name='book-detail'),
    
    # Borrowing endpoints
    path('borrow/', views.borrow_book, name='borrow-book'),
    path('return/', views.return_book, name='return-book'),
    
    # Admin borrowing endpoints
    path('admin/borrow/', views.admin_borrow_list, name='admin-borrow-list'),
    path('admin/borrow/<int:record_id>/approve/', views.approve_borrow_request, name='admin-approve-borrow'),
    path('admin/borrow/<int:record_id>/reject/', views.reject_borrow_request, name='admin-reject-borrow'),
] 