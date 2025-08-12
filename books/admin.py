from django.contrib import admin

from .models import Book, BorrowRecord


class BorrowRecordInline(admin.TabularInline):
    model = BorrowRecord
    extra = 0
    autocomplete_fields = ('user', 'book')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('user', 'book', 'status', 'borrow_date', 'return_date', 'created_at', 'updated_at')


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'quantity', 'created_at', 'updated_at')
    search_fields = ('title', 'author', 'genre')
    list_filter = ('genre',)
    ordering = ('title', 'author')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_display_links = ('title',)
    list_editable = ('genre', 'quantity')
    inlines = [BorrowRecordInline]


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'book', 'status', 'borrow_date', 'return_date', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'borrow_date', 'return_date')
    search_fields = ('user__username', 'book__title')
    autocomplete_fields = ('user', 'book')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'borrow_date'
    list_display_links = ('user', 'book')
    list_editable = ('status', 'borrow_date', 'return_date')
