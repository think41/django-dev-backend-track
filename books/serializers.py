from rest_framework import serializers

from .models import Book, BorrowRecord


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "genre", "quantity")


class BorrowRecordSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True, source="book")

    class Meta:
        model = BorrowRecord
        fields = (
            "id",
            "user",
            "book",
            "book_id",
            "status",
            "request_date",
            "borrow_date",
            "return_date",
        )

