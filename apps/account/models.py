from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Avg


def custom_user_img_upload_to(instance, filename):
    return f"users/{instance.id}/profile_images/{filename}"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    phone_number = models.CharField(max_length=20, blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    profile_picture = models.FileField(upload_to=custom_user_img_upload_to, blank=True)
    biography = models.TextField(blank=True)
    google_id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    # Role flags
    is_coach = models.BooleanField(default=False)
    is_gym_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    @property
    def rate(self):
        data = getattr(self, 'received_feedback', None)
        if data:
            avg = data.aggregate(rate=Avg('rating'))['rate']
            return round(avg, 2) if avg else 0.0
        return 0.0


class CoachProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coach_profile'
    )
    bio = models.TextField(blank=True)
    specialties = models.JSONField(default=list, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Coach: {self.user.full_name or self.user.email}"
