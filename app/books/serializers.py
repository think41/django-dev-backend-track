from rest_framework import serializers
from .models import Book
from app.users.models import BookRequest, BorrowHistory


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'publication_year', 'available_copies', 'summary']


class BookSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'genre', 'publication_year', 'available_copies']


class BookRequestSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    
    class Meta:
        model = BookRequest
        fields = ['id', 'book', 'book_title', 'book_author', 'request_date', 'borrow_date', 'return_date', 'status']
        read_only_fields = ['id', 'user', 'request_date', 'borrow_date', 'return_date', 'status']


class BorrowHistorySerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    
    class Meta:
        model = BorrowHistory
        fields = ['id', 'book_title', 'book_author', 'borrow_date', 'return_date']


class BookReturnSerializer(serializers.Serializer):
    book_request_id = serializers.UUIDField()