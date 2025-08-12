from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Book, BorrowRecord, Reservation, Fine

User = get_user_model()


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for Book model.
    """
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'genre', 'isbn', 'publication_date', 
                  'cover_image_url', 'quantity', 'created_at', 'updated_at')
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
    Used by members for creating borrow requests.
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
        fields = ('id', 'user', 'book', 'book_id', 'borrow_date', 'due_date', 'return_date', 
                  'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'borrow_date', 'due_date', 'return_date', 'status', 
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
        fields = ('id', 'user', 'book', 'borrow_date', 'due_date', 'return_date', 
                  'status', 'created_at', 'updated_at')
        read_only_fields = fields


class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializer for Reservation model.
    Used by members for creating and viewing reservations.
    """
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(),
        write_only=True,
        source='book'
    )
    book = BookBriefSerializer(read_only=True)
    user = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = Reservation
        fields = ('id', 'user', 'book', 'book_id', 'status', 'reservation_date', 
                  'notification_sent', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'status', 'reservation_date', 'notification_sent', 
                           'created_at', 'updated_at')


class FineSerializer(serializers.ModelSerializer):
    """
    Serializer for Fine model.
    Used by members for viewing their fines.
    """
    borrow_record = BorrowRecordSerializer(read_only=True)
    
    class Meta:
        model = Fine
        fields = ('id', 'borrow_record', 'user', 'amount', 'reason', 'status', 
                  'days_overdue', 'created_at', 'updated_at')
        read_only_fields = ('id', 'borrow_record', 'user', 'amount', 'reason', 
                           'days_overdue', 'created_at', 'updated_at')


class AdminFineSerializer(serializers.ModelSerializer):
    """
    Serializer for Fine model with expanded details.
    Used by admin for managing fines.
    """
    borrow_record = AdminBorrowRecordSerializer(read_only=True)
    user = UserBriefSerializer(read_only=True)
    
    class Meta:
        model = Fine
        fields = ('id', 'borrow_record', 'user', 'amount', 'reason', 'status', 
                  'days_overdue', 'created_at', 'updated_at')
        read_only_fields = ('id', 'borrow_record', 'user', 'amount', 'reason', 
                           'days_overdue', 'created_at', 'updated_at')
