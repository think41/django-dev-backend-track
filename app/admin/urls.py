from django.urls import path
from . import views

urlpatterns = [
    # Admin endpoints
    path('admin/', views.admin_users_list, name='admin_users_list'),
    path('admin/approve/', views.admin_approve_user, name='admin_approve_user'),

    path('admin/', views.admin_books, name='admin_books'),
    path('admin/<uuid:book_id>/', views.admin_book_detail, name='admin_book_detail'),
    path('admin/borrow-records/', views.admin_borrow_records, name='admin_borrow_records'),
    path('admin/approve-reject/', views.admin_approve_reject_request, name='admin_approve_reject_request'),
]