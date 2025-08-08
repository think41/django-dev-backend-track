"""
Django app configuration for the Authentication app.
"""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Configuration for the Authentication app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms.authentication'
    verbose_name = 'Authentication'