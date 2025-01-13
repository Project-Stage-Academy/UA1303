from functools import wraps

import jwt
from django.conf import settings
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of a startup to edit it
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


class IsRole(BasePermission):
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def get_user_role_from_token(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise PermissionDenied("Authorization header is missing or invalid (should be Bearer token).")

        token = auth_header.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            role = decoded_token.get('role')
            if not role:
                raise PermissionDenied("Role not found in token.")
            return role
        except jwt.ExpiredSignatureError:
            raise PermissionDenied("Token has expired. Please log in again.")
        except jwt.InvalidTokenError:
            raise PermissionDenied("Invalid token. Please log in with valid credentials.")

    def has_permission(self, request, view):
        user_role = self.get_user_role_from_token(request)
        if isinstance(self.allowed_roles, list):
            return user_role in self.allowed_roles
        else:
            return user_role == self.allowed_roles

def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(viewset_instance, request, *args, **kwargs):
            permission = IsRole(roles) # Створення екземпляра IsRole з передачею roles в конструктор
            if not permission.has_permission(request, viewset_instance):
                raise PermissionDenied("You do not have the necessary role for this action.")
            return view_func(viewset_instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator
