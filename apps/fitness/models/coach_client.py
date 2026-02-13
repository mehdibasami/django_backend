from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class CoachClient(models.Model):
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clients'
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coaches'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('coach', 'client')

    def clean(self):
        if not self.coach.is_coach:
            raise ValidationError("Coach user must have is_coach=True")
        if self.coach == self.client:
            raise ValidationError("Coach and client cannot be the same user")

    def __str__(self):
        return f"{self.coach} → {self.client}"
