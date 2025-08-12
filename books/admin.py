from django.contrib import admin

from .models import Book, BorrowRecord, Reservation, Fine


class BorrowRecordInline(admin.TabularInline):
    model = BorrowRecord
    extra = 0
    autocomplete_fields = ('user', 'book')
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'user', 'book', 'status', 'borrow_date', 'due_date', 'return_date', 'created_at', 'updated_at'
    )

class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 0
    autocomplete_fields = ('user', 'book')
    readonly_fields = ('reservation_date', 'created_at', 'updated_at')
    fields = (
        'user', 'book', 'status', 'reservation_date', 'notification_sent', 'created_at', 'updated_at'
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'genre', 'isbn', 'publication_date', 'quantity', 'created_at', 'updated_at'
    )
    search_fields = ('title', 'author', 'genre', 'isbn')
    list_filter = ('genre', 'publication_date')
    ordering = ('title', 'author')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_display_links = ('title',)
    list_editable = ('genre', 'quantity')
    inlines = [BorrowRecordInline, ReservationInline]


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'book', 'status', 'borrow_date', 'due_date', 'return_date', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'borrow_date', 'due_date', 'return_date')
    search_fields = ('user__username', 'book__title')
    autocomplete_fields = ('user', 'book')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'borrow_date'
    list_display_links = ('user', 'book')
    list_editable = ('status', 'borrow_date', 'return_date')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'book', 'status', 'reservation_date', 'notification_sent', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'reservation_date', 'notification_sent')
    search_fields = ('user__username', 'book__title')
    autocomplete_fields = ('user', 'book')
    readonly_fields = ('reservation_date', 'created_at', 'updated_at')
    date_hierarchy = 'reservation_date'
    list_display_links = ('user', 'book')
    list_editable = ('status', 'notification_sent')

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'borrow_record', 'amount', 'status', 'days_overdue', 'created_at', 'updated_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'borrow_record__book__title')
    autocomplete_fields = ('user', 'borrow_record')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    list_display_links = ('user', 'borrow_record')
    list_editable = ('status',)

