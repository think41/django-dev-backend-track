from django.contrib import admin
from .models import Book, BorrowRecord


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'quantity', 'created_at', 'updated_at')
    list_filter = ('genre', 'created_at', 'updated_at')
    search_fields = ('title', 'author', 'genre')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Book Information', {
            'fields': ('title', 'author', 'genre', 'quantity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'status', 'borrow_date', 'return_date', 'created_at')
    list_filter = ('status', 'borrow_date', 'return_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'book__title', 'book__author')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Borrow Information', {
            'fields': ('user', 'book', 'status')
        }),
        ('Dates', {
            'fields': ('borrow_date', 'return_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_requests', 'reject_requests', 'mark_as_returned']
    
    def approve_requests(self, request, queryset):
        """Admin action to approve pending borrow requests"""
        pending_requests = queryset.filter(status='PENDING')
        
        for record in pending_requests:
            if record.book.quantity > 0:
                record.status = 'APPROVED'
                record.borrow_date = record.updated_at.date()
                record.book.quantity -= 1
                record.book.save()
                record.save()
        
        count = pending_requests.count()
        self.message_user(
            request,
            f'{count} borrow request(s) were approved.'
        )
    approve_requests.short_description = "Approve selected pending requests"
    
    def reject_requests(self, request, queryset):
        """Admin action to reject pending borrow requests"""
        updated = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(
            request,
            f'{updated} borrow request(s) were rejected.'
        )
    reject_requests.short_description = "Reject selected pending requests"
    
    def mark_as_returned(self, request, queryset):
        """Admin action to mark approved requests as returned"""
        approved_requests = queryset.filter(status='APPROVED')
        
        for record in approved_requests:
            record.status = 'RETURNED'
            record.return_date = record.updated_at.date()
            record.book.quantity += 1
            record.book.save()
            record.save()
        
        count = approved_requests.count()
        self.message_user(
            request,
            f'{count} book(s) were marked as returned.'
        )
    mark_as_returned.short_description = "Mark selected books as returned"
