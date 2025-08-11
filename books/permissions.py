from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users with 'admin' role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsActiveUser(permissions.BasePermission):
    """
    Custom permission to only allow active users.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_active
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only admin users to create, update or delete objects.
    Read-only operations are allowed for authenticated users.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Allow GET, HEAD, OPTIONS requests for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Check if user is admin for other methods
        return request.user.role == 'admin'
