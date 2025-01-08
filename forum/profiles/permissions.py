from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

from users.utils import get_user_role_from_token


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of a startup to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request
        if request.method in SAFE_METHODS:
            return True

        # Handling anonymous users
        if request.user.is_anonymous:
            return False

        # safeguard to handle cases when object has no user attribute
        if not hasattr(obj, 'user'):
            return False

        # Write permissions are only allowed to the owner of the object
        return obj.user == request.user


class IsInvestor(BasePermission):
    """
    Custom permission to allow access only to users with 'investor' role
    """

    def has_permission(self, request, view):
        user_role = get_user_role_from_token(request)
        if not user_role or user_role != 'investor':
            raise PermissionDenied("Access denied. User must be an investor.")
        return True


class IsProfileUser(BasePermission):
    """
    Custom permission to allow access only to users with 'profile_user' role
    """

    def has_permission(self, request, view):
        user_role = get_user_role_from_token(request)
        if not user_role or user_role != 'profile_user':
            raise PermissionDenied("Access denied. User must be a profile user.")
        return True
