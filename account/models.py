from uuid import uuid4
from django.db.models import Avg

# Create your models here.
from django.db import models
from enum import Enum
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError


def custom_user_img_upload_to(instance, filename):
    return f"users/{instance.role}/u_{instance.id}/profile_images/{filename}"


class UserRole(Enum):
    client = 'Client'
    personal_trainer = 'Personal trainer'
    sports_coach = 'Sports coach'
    gym_manager = 'Gym manager'
    nutritionist = 'Nutritionist'
    health_professional = 'Health professional'

    @classmethod
    def choices(cls):
        return [(key.value, key.value) for key in cls]


# Address Model
class Address(models.Model):
    city = models.CharField(max_length=255, blank=True, default='')
    province = models.CharField(max_length=255, blank=True, default='')
    address = models.TextField(
        blank=True,
        default=''
    )
    zip_code = models.CharField(max_length=20, blank=True, default='')

    def __str__(self):
        return f"{self.address}, {self.city}, {self.province}, {self.zip_code}"


# User Model
class User(AbstractUser):

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )
    email = models.EmailField(unique=True, max_length=255)
    phone_number = models.CharField(max_length=20,  blank=True)
    google_id = models.CharField(
        null=True,
        blank=True
    )
    is_email_confirmed = models.BooleanField(
        default=False,
    )
    # reset_password_token = models.UUIDField(
    #     primary_key=False,
    #     editable=False,
    #     default=uuid4
    # )
    full_name = models.CharField(max_length=255, blank=True, default='')
    fcm_token = ArrayField(
        models.TextField(),
        blank=True,
        default=list
    )
    gender = models.CharField(max_length=20, blank=True, default='')
    birth_date = models.DateField(null=True, blank=True, default=None)
    profile_picture = models.FileField(
        upload_to=custom_user_img_upload_to,
        blank=True,
        default=''
    )
    address = models.OneToOneField(
        Address,
        on_delete=models.SET_NULL,
        null=True,
    )
    biography = models.TextField(blank=True, default='')
    role = models.CharField(max_length=50, choices=UserRole.choices(), default=UserRole.client.value)
    # client details
    trainers = models.ManyToManyField(
        'self',
        symmetrical=False,
        limit_choices_to={'role': UserRole.personal_trainer.value},
        related_name='clients',
        through='ClientTrainerRelationship'
    )
    # Business details
    skills = ArrayField(base_field=models.CharField(max_length=255, blank=True), blank=True, default=list)
    company_name = models.CharField(max_length=255, blank=True, default='')
    company_website = models.URLField(blank=True, default='')
    years_of_experience = models.IntegerField(blank=True, default=0)
    allow_share_progress = models.BooleanField(default=False)

    @property
    def rate(self):

        data = self.received_feedback.aggregate(rate=Avg('rating'))
        if data['rate'] is None:
            return 0.0
        return round(data['rate'], 2)


class ClientTrainerRelationship(models.Model):
    client = models.ForeignKey('User', on_delete=models.CASCADE, related_name='trainer_links')
    trainer = models.ForeignKey('User', on_delete=models.CASCADE, related_name='client_links')
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('client', 'trainer')

    def clean(self):
        from .models import UserRole
        if self.trainer.role != UserRole.personal_trainer.value:
            raise ValidationError("Assigned trainer must have role 'PersonalTrainer'.")
        if self.client.role != UserRole.client.value:
            raise ValidationError("Assigned client must have role 'Client'.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
