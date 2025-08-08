"""
Django app configuration for the Users app.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for the Users app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms.users'
    verbose_name = 'User Management'