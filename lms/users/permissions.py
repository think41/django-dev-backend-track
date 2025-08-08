"""
Custom permissions for the Users app.

This module defines custom permission classes used to control access
to various endpoints based on user roles and status.
"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permission class that only allows access to admin users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN' and
            request.user.status == 'ACTIVE'
        )


class IsActiveMember(BasePermission):
    """
    Permission class that only allows access to active members.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'MEMBER' and
            request.user.status == 'ACTIVE'
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Permission class that allows access to the owner of the resource or admin users.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object
        if request.user.role == 'ADMIN':
            return True
        
        # Users can only access their own objects
        return obj == request.user


class IsActiveUser(BasePermission):
    """
    Permission class that only allows access to active users (both admin and members).
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.status == 'ACTIVE'
        )