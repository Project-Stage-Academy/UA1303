from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import AccessToken
from .models import Role

class BaseRolePermission(BasePermission):
    """
    Permission class to check if a user has the required role,
    based on both the token and the database state.
    """
    required_role: Role

    def has_permission(self, request: Request, view) -> bool:
        if not request.user.is_authenticated:
            return False

        if not isinstance(request.auth, AccessToken) or request.auth is None:
            raise PermissionDenied("Something is wrong with auth: user's probably not using JWT or another problem")

        token_role = request.auth.get('role')

        if self.required_role == Role.UNASSIGNED:
            return token_role == Role.UNASSIGNED.value

        ROLE_ALIGNS = token_role == self.required_role.value
        USER_HAS_ROLE = Role.has_role(user_role=request.user.role, role=self.required_role)

        return ROLE_ALIGNS and USER_HAS_ROLE


class IsInvestor(BaseRolePermission):
    required_role = Role.INVESTOR


class IsStartup(BaseRolePermission):
    required_role = Role.STARTUP