from rest_framework.permissions import BasePermission


class Unassigned(BasePermission):
    def has_permission(self, request, view):
        return request.auth.get('role') == 'unassigned'


class IsInvestor(BasePermission):
    def has_permission(self, request, view):
        return request.auth.get('role') == 'investor'


class IsStartup(BasePermission):
    def has_permission(self, request, view):
        return request.auth.get('role') == 'startup'