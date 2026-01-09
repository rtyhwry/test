"""Custom permissions for the platform."""
from rest_framework import permissions


class IsAdminOrManager(permissions.BasePermission):
    """Permission for admin or manager users."""
    
    def has_permission(self, request, view):
        """Check if user is admin or manager."""
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'manager']


class IsAdminOrManagerOrOwner(permissions.BasePermission):
    """Permission for admin, manager, or object owner."""
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permission."""
        if not request.user.is_authenticated:
            return False
        
        # Admin and manager can access everything
        if request.user.role in ['admin', 'manager']:
            return True
        
        # Check if user is owner
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False


class IsEngineerOrAbove(permissions.BasePermission):
    """Permission for engineer or above roles."""
    
    def has_permission(self, request, view):
        """Check if user is engineer or above."""
        if not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'manager', 'engineer']
