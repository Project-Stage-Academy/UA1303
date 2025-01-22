from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS
from users.models import Role


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


class AbstractRolePermission(BasePermission):
    role = None

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.auth or not hasattr(request.auth, "get"):
            raise AuthenticationFailed("Invalid or missing token")

        token_role_value = request.auth.get('role')
        if not token_role_value or not str(token_role_value).isdigit():
            raise AuthenticationFailed("Invalid role in token")

        return int(token_role_value) == self.role


class IsStartup(AbstractRolePermission):
    role = Role.STARTUP.value


class IsInvestor(AbstractRolePermission):
    role = Role.INVESTOR.value
