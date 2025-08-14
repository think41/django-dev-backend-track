from django.contrib import admin
from .models import Book, BorrowRecord


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'quantity', 'created_at')
    list_filter = ('genre', 'created_at')
    search_fields = ('title', 'author', 'genre')
    ordering = ('-created_at',)


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'status', 'borrow_date', 'return_date', 'created_at')
    list_filter = ('status', 'borrow_date', 'return_date', 'created_at')
    search_fields = ('user__username', 'book__title')
    ordering = ('-created_at',)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ('user', 'book', 'created_at')
        return ('created_at',) 