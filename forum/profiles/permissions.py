from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read-only permissions are allowed for any request
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return obj.owner == request.user

