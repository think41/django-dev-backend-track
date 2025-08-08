"""
Serializers for the Users app.

This module contains all serializers for user-related API endpoints,
including user management, profile updates, and borrowing functionality.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs
    
    def create(self, validated_data):
        """Create a new user with encrypted password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            status='PENDING'  # All new users start as pending
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information."""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'status', 'date_joined')
        read_only_fields = ('id', 'username', 'role', 'status', 'date_joined')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ('email',)


class AdminUserListSerializer(serializers.ModelSerializer):
    """Serializer for admin user list view."""
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'role', 'status', 
            'date_joined', 'borrowed_books'
        )
        read_only_fields = ('id', 'date_joined')


class BorrowRequestSerializer(serializers.Serializer):
    """Serializer for book borrow requests."""
    
    book_id = serializers.IntegerField()
    
    def validate_book_id(self, value):
        """Validate that the book exists and is available."""
        from lms.books.models import Book
        
        try:
            book = Book.objects.get(id=value)
            if book.available_copies <= 0:
                raise serializers.ValidationError(
                    "This book is currently not available."
                )
        except Book.DoesNotExist:
            raise serializers.ValidationError("Book not found.")
        
        return value


class BorrowHistorySerializer(serializers.Serializer):
    """Serializer for borrowing history."""
    
    book_id = serializers.IntegerField()
    book_title = serializers.CharField()
    request_date = serializers.DateTimeField()
    approval_date = serializers.DateTimeField(allow_null=True)
    return_date = serializers.DateTimeField(allow_null=True)
    due_date = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()


class BorrowRecordSerializer(serializers.Serializer):
    """Serializer for admin borrow record views."""
    
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    book_id = serializers.IntegerField()
    book_title = serializers.CharField()
    request_date = serializers.DateTimeField()
    approval_date = serializers.DateTimeField(allow_null=True)
    return_date = serializers.DateTimeField(allow_null=True)
    due_date = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()


class BorrowApprovalSerializer(serializers.Serializer):
    """Serializer for borrow request approval."""
    
    due_date = serializers.DateTimeField(required=False)
    
    def validate_due_date(self, value):
        """Validate that due date is in the future."""
        from datetime import datetime
        
        if value and value <= datetime.now():
            raise serializers.ValidationError(
                "Due date must be in the future."
            )
        return value