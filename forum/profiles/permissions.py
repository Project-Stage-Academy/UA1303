from rest_framework.permissions import BasePermission, SAFE_METHODS


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

