"""
URL configuration for Library Management System (LMS) project.

This module defines the main URL routing for the LMS API endpoints.
All API endpoints are organized under the /api/ prefix.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def api_root(request):
    """Root API endpoint with information about available endpoints."""
    return JsonResponse({
        'message': 'Welcome to Library Management System API',
        'version': '1.0',
        'endpoints': {
            'authentication': '/api/auth/',
            'users': '/api/users/',
            'books': '/api/books/',
            'admin_panel': '/admin/',
            'api_docs': '/api/docs/',  # For future API documentation
        },
        'status': 'active'
    })


urlpatterns = [
    # Django Admin Panel
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api-root'),
    
    # Authentication endpoints
    path('api/auth/', include('lms.authentication.urls')),
    
    # User management endpoints
    path('api/users/', include('lms.users.urls')),
    
    # Book management endpoints
    path('api/books/', include('lms.books.urls')),
]

# Add debug toolbar URLs for development (if installed)
import sys
if 'runserver' in sys.argv:
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
