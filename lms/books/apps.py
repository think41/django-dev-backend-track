"""
Django app configuration for the Books app.
"""

from django.apps import AppConfig


class BooksConfig(AppConfig):
    """Configuration for the Books app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lms.books'
    verbose_name = 'Book Management'