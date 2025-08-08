from rest_framework import serializers
from .models import Book, BorrowRecord
from users.serializers import UserSerializer


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'genre', 'quantity', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title', 'author', 'genre', 'quantity')


class BorrowRequestSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()


class ReturnBookSerializer(serializers.Serializer):
    borrow_record_id = serializers.IntegerField()


class BorrowRecordSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    
    class Meta:
        model = BorrowRecord
        fields = ('id', 'user', 'book', 'borrow_date', 'return_date', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'book', 'created_at', 'updated_at')


class BooksMessageResponseSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Response message")
    
    class Meta:
        ref_name = "BooksMessageResponse"