from django.urls import path
from . import views

urlpatterns = [
    # Book Catalog Operations - Combined view for GET and POST
    path('list/', views.list_books, name='list_books'),  # GET /api/books/list/
    path('create/', views.create_book, name='create_book'),  # POST /api/books/create/
    path('<int:book_id>/', views.get_book, name='get_book'),  # GET /api/books/{id}/
    path('<int:book_id>/update/', views.update_book, name='update_book'),  # PUT /api/books/{id}/update/
    path('<int:book_id>/delete/', views.delete_book, name='delete_book'),  # DELETE /api/books/{id}/delete/
    
    # Member Borrowing Operations
    path('borrow/', views.borrow_book, name='borrow_book'),  # POST /api/books/borrow/
    path('return/', views.return_book, name='return_book'),  # POST /api/books/return/
    
    # Admin Borrow Management
    path('admin/borrow/', views.list_borrow_records, name='list_borrow_records'),  # GET /api/books/admin/borrow/
    path('admin/borrow/<int:record_id>/approve/', views.approve_borrow_request, name='approve_borrow_request'),  # PATCH /api/books/admin/borrow/{id}/approve/
    path('admin/borrow/<int:record_id>/reject/', views.reject_borrow_request, name='reject_borrow_request'),  # PATCH /api/books/admin/borrow/{id}/reject/
]