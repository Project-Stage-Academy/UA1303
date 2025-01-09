# forum/notifications/permissions.py
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import StartUpNotification

class HasStartupProfilePermission(permissions.BasePermission):
    """
    Custom permission class to check if a user has a startup profile.
    """
    def has_permission(self, request, view):
        if not hasattr(request.user, 'startup_profile'):
            raise NotFound("User does not have a startup profile.")
        return True

class HasStartupAccessPermission(permissions.BasePermission):
    """
    Custom permission class to check if a user has access to a specific startup profile.
    """
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, StartUpNotification):
            if request.user.startup_profile.id != obj.startup_id:
                raise PermissionDenied("Access denied")
        return True