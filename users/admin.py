from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


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
