from rest_framework import serializers
from ..models import Book, BorrowRecord, Fine


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "genre",
            "isbn",
            "publisher",
            "publication_date",
            "cover_image_url",
            "available_copies",
            "created_at",
            "updated_at",
        )


class BorrowRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRecord
        fields = (
            "id",
            "user",
            "book",
            "borrow_date",
            "return_date",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("user", "borrow_date", "return_date", "status")


class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fine
        fields = (
            "id",
            "borrow_record",
            "amount",
            "reason",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("reason", "created_at", "updated_at")
