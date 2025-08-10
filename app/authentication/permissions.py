from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to perform certain actions.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'Admin'


class IsMemberUser(permissions.BasePermission):
    """
    Custom permission to only allow member users to perform certain actions.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'Member'


class IsApprovedUser(permissions.BasePermission):
    """
    Custom permission to only allow approved users to perform certain actions.
    """

    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_approved
        )