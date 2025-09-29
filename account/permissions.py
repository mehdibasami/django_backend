from rest_framework import permissions
from account.models import UserRole


class IsActiveUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_active


class CanAssignWorkoutProgram(permissions.BasePermission):
    """
    Allows only users with roles:
      - personal_trainer
      - sports_coach
      - health_professional
    to assign workout programs.
    """

    def has_permission(self, request, view):
        # Make sure the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Allowed roles (matching the enum .name values)
        allowed = {
            UserRole.personal_trainer.value,
            UserRole.sports_coach.value,
            UserRole.health_professional.value,
        }
        return request.user.role in allowed
