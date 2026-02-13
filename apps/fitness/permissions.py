from rest_framework.permissions import BasePermission


class IsProgramOwner(BasePermission):
    """
    Allows access only to the user who created the program.
    """

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user
