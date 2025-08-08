"""
Django admin configuration for the Users app.

This module configures the Django admin interface for user management,
providing a comprehensive interface for admins to manage users and
view borrowing records.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    """Custom User admin configuration."""
    
    # Display fields in the user list
    list_display = (
        'username', 'email', 'role', 'status', 'date_joined',
        'borrowed_books_count', 'is_staff'
    )
    
    # Filters for the user list
    list_filter = (
        'role', 'status', 'is_staff', 'is_superuser', 
        'is_active', 'date_joined'
    )
    
    # Search fields
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Ordering
    ordering = ('-date_joined',)
    
    # Fields to display when editing a user
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Library Management', {
            'fields': ('role', 'status', 'borrowed_books_display'),
        }),
    )
    
    # Fields to display when adding a user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Library Management', {
            'fields': ('email', 'role', 'status'),
        }),
    )
    
    # Read-only fields
    readonly_fields = ('borrowed_books_display', 'date_joined')
    
    def borrowed_books_count(self, obj):
        """Display the number of borrowed books."""
        count = len(obj.borrowed_books) if obj.borrowed_books else 0
        if count == 0:
            return "No borrowings"
        return f"{count} records"
    borrowed_books_count.short_description = "Borrowing Records"
    
    def borrowed_books_display(self, obj):
        """Display borrowed books in a formatted way."""
        if not obj.borrowed_books:
            return "No borrowing history"
        
        html = "<div style='max-height: 300px; overflow-y: auto;'>"
        html += "<table style='width: 100%; border-collapse: collapse;'>"
        html += """
        <tr style='background-color: #f0f0f0; font-weight: bold;'>
            <th style='padding: 5px; border: 1px solid #ddd;'>Book ID</th>
            <th style='padding: 5px; border: 1px solid #ddd;'>Status</th>
            <th style='padding: 5px; border: 1px solid #ddd;'>Request Date</th>
            <th style='padding: 5px; border: 1px solid #ddd;'>Due Date</th>
        </tr>
        """
        
        for record in obj.borrowed_books:
            status_color = {
                'PENDING': '#ff9800',
                'APPROVED': '#4caf50', 
                'REJECTED': '#f44336',
                'RETURNED': '#2196f3'
            }.get(record.get('status', 'UNKNOWN'), '#666')
            
            html += f"""
            <tr>
                <td style='padding: 5px; border: 1px solid #ddd;'>{record.get('book_id', 'N/A')}</td>
                <td style='padding: 5px; border: 1px solid #ddd; color: {status_color}; font-weight: bold;'>
                    {record.get('status', 'UNKNOWN')}
                </td>
                <td style='padding: 5px; border: 1px solid #ddd;'>{record.get('request_date', 'N/A')[:10]}</td>
                <td style='padding: 5px; border: 1px solid #ddd;'>{record.get('due_date', 'N/A')[:10] if record.get('due_date') else 'N/A'}</td>
            </tr>
            """
        
        html += "</table></div>"
        return mark_safe(html)
    borrowed_books_display.short_description = "Borrowing History"
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure admin users have proper permissions."""
        super().save_model(request, obj, form, change)
        # The model's save method will handle setting is_staff and is_superuser
    
    actions = ['approve_pending_users', 'suspend_users', 'activate_users']
    
    def approve_pending_users(self, request, queryset):
        """Bulk action to approve pending users."""
        updated = queryset.filter(status='PENDING').update(status='ACTIVE')
        self.message_user(
            request, 
            f"{updated} users were successfully approved."
        )
    approve_pending_users.short_description = "Approve selected pending users"
    
    def suspend_users(self, request, queryset):
        """Bulk action to suspend users."""
        updated = queryset.exclude(status='SUSPENDED').update(status='SUSPENDED')
        self.message_user(
            request,
            f"{updated} users were successfully suspended."
        )
    suspend_users.short_description = "Suspend selected users"
    
    def activate_users(self, request, queryset):
        """Bulk action to activate users."""
        updated = queryset.exclude(status='ACTIVE').update(status='ACTIVE')
        self.message_user(
            request,
            f"{updated} users were successfully activated."
        )
    activate_users.short_description = "Activate selected users"


# Register the custom User admin
admin.site.register(User, UserAdmin)

# Customize admin site header
admin.site.site_header = "Library Management System Administration"
admin.site.site_title = "LMS Admin"
admin.site.index_title = "Welcome to Library Management System Administration"