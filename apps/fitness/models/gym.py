from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def custom_gym_img_upload_to(instance, filename):
    return f"gyms/{instance.id}/{filename}"


class Gym(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_gyms'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.FileField(upload_to=custom_gym_img_upload_to, blank=True)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class CoachGym(models.Model):
    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gyms_as_coach'
    )
    gym = models.ForeignKey(
        Gym,
        on_delete=models.CASCADE,
        related_name='coaches'
    )

    class Meta:
        unique_together = ('coach', 'gym')

    def __str__(self):
        return f"{self.coach} @ {self.gym}"

    def clean(self):
        if not self.coach.is_coach:
            raise ValidationError("User must be a coach to be assigned to a gym")
