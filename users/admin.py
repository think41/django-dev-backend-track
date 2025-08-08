from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    # Fields to display in the user detail/edit form
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Library System', {
            'fields': ('role',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Fields to display when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_active'),
        }),
    )
    
    # Enable actions
    actions = ['approve_users', 'deactivate_users']
    
    def approve_users(self, request, queryset):
        """Admin action to approve (activate) selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} user(s) were successfully approved and activated.'
        )
    approve_users.short_description = "Approve selected users"
    
    def deactivate_users(self, request, queryset):
        """Admin action to deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} user(s) were successfully deactivated.'
        )
    deactivate_users.short_description = "Deactivate selected users"
    
    # Custom methods for list display
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()
    
    # Add custom styling for roles and status
    def role(self, obj):
        if obj.role == 'admin':
            return '🔧 Admin'
        elif obj.role == 'member':
            return '👤 Member'
        return obj.role
    role.short_description = 'Role'
    
    def is_active(self, obj):
        return '✅ Active' if obj.is_active else '❌ Inactive'
    is_active.short_description = 'Status'
    is_active.boolean = True
