from rest_framework.permissions import BasePermission


class IsFindingHandler(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('findings.handle_findings')
