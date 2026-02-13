from django.db import models
from django.conf import settings
from uuid import uuid4


class ProgramAssignmentAudit(models.Model):
    """
    Immutable audit log for program assignment actions
    """

    class Action(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        UNASSIGNED = "UNASSIGNED", "Unassigned"
        REASSIGNED = "REASSIGNED", "Reassigned"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assignment_actions"
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assignment_audits"
    )

    program = models.ForeignKey(
        "fitness.WorkoutProgram",
        on_delete=models.SET_NULL,
        null=True
    )

    assignment = models.ForeignKey(
        "fitness.ProgramAssignment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(
        max_length=20,
        choices=Action.choices
    )

    meta = models.JSONField(blank=True, default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} → {self.client} ({self.program})"
