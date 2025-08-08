"""
Django admin configuration for the Books app.

This module configures the Django admin interface for book management,
providing a comprehensive interface for admins to manage book inventory.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Custom Book admin configuration."""
    
    # Display fields in the book list
    list_display = (
        'title', 'author', 'genre', 'availability_status',
        'total_copies', 'available_copies', 'borrowed_copies_display',
        'created_at'
    )
    
    # Filters for the book list
    list_filter = (
        'genre', 'created_at',
        ('available_copies', admin.EmptyFieldListFilter),
    )
    
    # Search fields
    search_fields = ('title', 'author', 'genre')
    
    # Ordering
    ordering = ('title',)
    
    # Fields to display when editing a book
    fields = (
        'title', 'author', 'genre', 'total_copies', 
        'available_copies', 'inventory_info'
    )
    
    # Read-only fields
    readonly_fields = ('inventory_info',)
    
    # Fields that can be edited in the list view
    list_editable = ('total_copies',)
    
    def availability_status(self, obj):
        """Display availability status with color coding."""
        if obj.available_copies > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">Available ({})</span>',
                obj.available_copies
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">Not Available</span>'
            )
    availability_status.short_description = "Availability"
    availability_status.admin_order_field = 'available_copies'
    
    def borrowed_copies_display(self, obj):
        """Display borrowed copies with visual indicator."""
        borrowed = obj.borrowed_copies
        if borrowed == 0:
            return format_html(
                '<span style="color: gray;">0</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{}</span>',
                borrowed
            )
    borrowed_copies_display.short_description = "Borrowed"
    
    def inventory_info(self, obj):
        """Display detailed inventory information."""
        if not obj.id:
            return "Save the book to see inventory information."
        
        borrowed_percentage = (obj.borrowed_copies / obj.total_copies) * 100 if obj.total_copies > 0 else 0
        
        return format_html(
            """
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                <strong>Inventory Status:</strong><br/>
                Total Copies: {}<br/>
                Available: {} ({:.1f}%)<br/>
                Borrowed: {} ({:.1f}%)<br/>
                <div style="margin-top: 5px;">
                    <div style="background-color: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden;">
                        <div style="background-color: {}; height: 100%; width: {:.1f}%; transition: width 0.3s;"></div>
                    </div>
                    <small style="color: #6c757d;">Utilization: {:.1f}%</small>
                </div>
            </div>
            """,
            obj.total_copies,
            obj.available_copies,
            (obj.available_copies / obj.total_copies) * 100 if obj.total_copies > 0 else 0,
            obj.borrowed_copies,
            borrowed_percentage,
            '#28a745' if borrowed_percentage < 50 else '#ffc107' if borrowed_percentage < 80 else '#dc3545',
            borrowed_percentage,
            borrowed_percentage
        )
    inventory_info.short_description = "Inventory Information"
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure data consistency."""
        # Ensure available_copies doesn't exceed total_copies
        if obj.available_copies > obj.total_copies:
            obj.available_copies = obj.total_copies
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        """Make available_copies readonly for existing books with borrowings."""
        readonly_fields = list(self.readonly_fields)
        
        if obj and obj.borrowed_copies > 0:
            readonly_fields.append('available_copies')
            
        return readonly_fields
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form help texts and widgets."""
        form = super().get_form(request, obj, **kwargs)
        
        if 'total_copies' in form.base_fields:
            if obj and obj.borrowed_copies > 0:
                form.base_fields['total_copies'].help_text = (
                    f"Currently {obj.borrowed_copies} copies are borrowed. "
                    f"Total copies cannot be less than borrowed copies."
                )
            else:
                form.base_fields['total_copies'].help_text = (
                    "Total number of copies in the library inventory."
                )
        
        if 'available_copies' in form.base_fields:
            if obj and obj.borrowed_copies > 0:
                form.base_fields['available_copies'].help_text = (
                    "This field is readonly when books are borrowed. "
                    "Available copies will be updated when books are returned."
                )
        
        return form
    
    # Custom admin actions
    actions = ['mark_as_unavailable', 'restore_availability']
    
    def mark_as_unavailable(self, request, queryset):
        """Mark selected books as temporarily unavailable."""
        updated = 0
        for book in queryset:
            if book.available_copies > 0:
                book.available_copies = 0
                book.save()
                updated += 1
        
        self.message_user(
            request,
            f"{updated} books were marked as unavailable."
        )
    mark_as_unavailable.short_description = "Mark selected books as unavailable"
    
    def restore_availability(self, request, queryset):
        """Restore full availability for selected books."""
        updated = 0
        for book in queryset:
            if book.available_copies < book.total_copies:
                book.available_copies = book.total_copies
                book.save()
                updated += 1
        
        self.message_user(
            request,
            f"{updated} books had their availability restored."
        )
    restore_availability.short_description = "Restore full availability for selected books"
    
    def changelist_view(self, request, extra_context=None):
        """Add summary statistics to the changelist view."""
        extra_context = extra_context or {}
        
        # Calculate summary statistics
        total_books = Book.objects.count()
        total_copies = sum(Book.objects.values_list('total_copies', flat=True))
        available_copies = sum(Book.objects.values_list('available_copies', flat=True))
        borrowed_copies = total_copies - available_copies
        
        extra_context['summary_stats'] = {
            'total_books': total_books,
            'total_copies': total_copies,
            'available_copies': available_copies,
            'borrowed_copies': borrowed_copies,
            'utilization_rate': (borrowed_copies / total_copies * 100) if total_copies > 0 else 0
        }
        
        return super().changelist_view(request, extra_context=extra_context)