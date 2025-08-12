from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User
from books.models import BorrowRecord, Reservation, Fine


class BorrowRecordInline(admin.TabularInline):
    model = BorrowRecord
    extra = 0
    autocomplete_fields = ('book',)
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'book', 'status', 'borrow_date', 'due_date', 'return_date', 'created_at', 'updated_at'
    )


class ReservationInline(admin.TabularInline):
    model = Reservation
    extra = 0
    autocomplete_fields = ('book',)
    readonly_fields = ('reservation_date', 'created_at', 'updated_at')
    fields = (
        'book', 'status', 'reservation_date', 'notification_sent', 'created_at', 'updated_at'
    )


class FineInline(admin.TabularInline):
    model = Fine
    extra = 0
    autocomplete_fields = ('borrow_record',)
    readonly_fields = ('created_at', 'updated_at')
    fields = ('borrow_record', 'amount', 'status', 'days_overdue', 'reason', 'created_at', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin for the custom User model, extending Django's default UserAdmin."""
    # Show useful columns in the changelist
    list_display = (
        'username', 'email', 'role', 'is_active', 'is_staff', 'is_superuser', 'date_joined',
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    inlines = [BorrowRecordInline, ReservationInline, FineInline]

    # Include our custom fields in the edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            'Additional info',
            {
                'fields': ('role',),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            'Additional info',
            {
                'classes': ('wide',),
                'fields': ('email', 'role'),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        """Ensure email is required on add user form."""
        form = super().get_form(request, obj, **kwargs)
        if 'email' in form.base_fields:
            form.base_fields['email'].required = True
        return form
