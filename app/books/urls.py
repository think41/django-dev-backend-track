from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_books, name='search_books'),
    path('request/', views.request_book, name='request_book'),
    path('return/', views.return_book, name='return_book'),
    path('history/', views.borrowing_history, name='borrowing_history'),
    path('requests/', views.borrow_requests, name='borrow_requests'),
]