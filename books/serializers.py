from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Book, BorrowRecord

User = get_user_model()


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for Book model.
    Used for CRUD operations on books.
    """
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'genre', 'quantity', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserBriefSerializer(serializers.ModelSerializer):
    """
    Brief serializer for User model.
    Used in nested serializations.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = fields


class BookBriefSerializer(serializers.ModelSerializer):
    """
    Brief serializer for Book model.
    Used in nested serializations.
    """
    class Meta:
        model = Book
        fields = ('id', 'title', 'author')
        read_only_fields = fields


class BorrowRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for BorrowRecord model.
    Used for creating and retrieving borrow records.
    """
    user = UserBriefSerializer(read_only=True)
    book = BookBriefSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        write_only=True,
        source='book'
    )
    
    class Meta:
        model = BorrowRecord
        fields = ('id', 'user', 'book', 'book_id', 'borrow_date', 'return_date', 
                  'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'borrow_date', 'return_date', 'status', 
                           'created_at', 'updated_at')


class AdminBorrowRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for BorrowRecord model with expanded details.
    Used by admin for managing borrow records.
    """
    user = UserBriefSerializer(read_only=True)
    book = BookBriefSerializer(read_only=True)
    
    class Meta:
        model = BorrowRecord
        fields = ('id', 'user', 'book', 'borrow_date', 'return_date', 
                  'status', 'created_at', 'updated_at')
        read_only_fields = fields
