from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from .models import Role, CustomUser

class HasRole(BasePermission):
    """
    Permission class to check if a user has the required role,
    based on both the token and the database state.
    """

    def __init__(self, role: Role):
        self.role = role

    def has_permission(self, request: Request, view) -> bool:
        if not request.user.is_authenticated:
            return False

        try:
            token_role = request.auth.get('role')
        except AttributeError as e:
            return False

        if self.role == Role.UNASSIGNED:
            return token_role == Role.UNASSIGNED.value

        role_aligns = token_role == self.role.value
        user_has_role = Role.has_role(user_role=request.user.role, role=self.role)

        return role_aligns and user_has_role
