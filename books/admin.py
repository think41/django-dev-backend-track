from django.contrib import admin

from .models import Book, BorrowRecord


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "genre", "quantity", "created_at")
    search_fields = ("title", "author", "genre")


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "status", "request_date", "borrow_date", "return_date")
    list_filter = ("status",)
    search_fields = ("user__username", "book__title")

