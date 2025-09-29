from django.db import models
from uuid import uuid4
from account.models import User
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField
from enum import Enum


def exercise_image_upload_to(instance, filename):

    uid = instance.exercise.created_by.id
    role = instance.exercise.created_by.role
    exercise_id = instance.exercise.id
    return f'users/{role}/u_{uid}/workout/exercises/{exercise_id}/images/{filename}'


def exercise_video_upload_to(instance, filename):
    exercise_id = instance.id
    uid = instance.created_by.id
    role = instance.created_by.role
    return f'users/{role}/u_{uid}/workout/exercises/{exercise_id}/videos/{filename}'


def program_image_upload_to(instance, filename):

    uid = instance.program.carpenter.id
    role = instance.program.created_by.role
    program_id = instance.program.id
    return f'users/{role}/u_{uid}/workout/programs/{program_id}/images/{filename}'


def program_video_upload_to(instance, filename):
    program_id = instance.id
    uid = instance.created_by.id
    role = instance.created_by.role
    return f'users/{role}/u_{uid}/exercise/{program_id}/videos/{filename}'


def session_image_upload_to(instance, filename):

    uid = instance.session.created_by.id
    role = instance.session.created_by.role
    session_id = instance.session.id
    return f'users/{role}/u_{uid}/workout/sessions/{session_id}/images/{filename}'


def session_video_upload_to(instance, filename):
    session_id = instance.id
    uid = instance.created_by.id
    role = instance.created_by.role
    return f'users/{role}/u_{uid}/workout/sessions/{session_id}/videos/{filename}'


class Category(models.Model):
    id = models.CharField(max_length=24, primary_key=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Modality(models.Model):
    id = models.CharField(max_length=24, primary_key=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Equipment(models.Model):
    id = models.CharField(max_length=24, primary_key=True)
    title = models.CharField(max_length=255)
    icon = models.URLField(blank=True)

    def __str__(self):
        return self.title


class MuscleGroup(models.Model):
    id = models.CharField(max_length=24, primary_key=True)
    title = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='subgroups'
    )

    def __str__(self):
        return self.title


class TrainingSystem(models.Model):
    id = models.CharField(max_length=24, primary_key=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Exercise(models.Model):
    @property
    def all_images(self):
        """Returns all images associated with this project."""
        return self.images.all()

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, default='')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    instructions = ArrayField(
        models.TextField(blank=True),
        default=list,
        blank=True,
    )
    # self-referential alternatives
    alternatives = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
    )
    muscle_groups = models.ManyToManyField(
        MuscleGroup,
        through='ExerciseMuscleGroup',
        related_name='exercises',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exercises'
    )
    modalities = models.ManyToManyField(
        Modality,
        blank=True,
        related_name='exercises'
    )
    training_system = models.ForeignKey(
        TrainingSystem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='exercises'
    )
    video = models.FileField(upload_to=exercise_video_upload_to, blank=True, null=True)
    level = models.CharField(max_length=50, blank=True)
    intensity = models.CharField(max_length=50, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercises')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)
    is_multiple_exercise = models.BooleanField(default=False)
    popularity = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ExerciseMuscleGroup(models.Model):
    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='exercise_muscle_entries'
    )
    muscle_group = models.ForeignKey(
        MuscleGroup,
        on_delete=models.CASCADE
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('exercise', 'muscle_group')

    def __str__(self):
        return f"{self.exercise.name} → {self.muscle_group.title} ({'primary' if self.is_primary else 'secondary'})"


class WorkoutProgram(models.Model):
    @property
    def all_images(self):
        """Returns all images associated with this project."""
        return self.images.all()

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, default='')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='programs', null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_programs', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    off_percent = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    duration = models.CharField(max_length=50, blank=True)
    level = models.CharField(max_length=50, blank=True)
    handle = models.CharField(max_length=255, unique=True)
    video = models.FileField(upload_to=program_video_upload_to, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    equipment = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class WorkoutSession(models.Model):
    @property
    def all_images(self):
        """Returns all images associated with this project."""
        return self.images.all()

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    program = models.ForeignKey(WorkoutProgram, on_delete=models.SET_NULL, related_name='sessions', null=True)
    day_title = models.CharField(max_length=100, blank=True, default='')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    notes = models.TextField(blank=True, default='')
    week_number = models.PositiveIntegerField(default=1)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sessions', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    equipments = models.CharField(max_length=255, blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    is_rest_day = models.BooleanField(default=False)
    session_type = models.CharField(max_length=100, blank=True)
    video = models.FileField(upload_to=session_video_upload_to, blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True)
    intensity = models.CharField(max_length=50, blank=True)
    popularity = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.day_title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.day_title} - {self.program.title if self.program else 'No Program'}"


class WorkoutExercise(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    duration = models.CharField(max_length=50, blank=True)
    rest_time = models.CharField(max_length=50, blank=True)
    tempo = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.exercise.name} - {self.sets}x{self.reps}"


class UserWorkoutProgram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey("WorkoutProgram", on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-assigned_at']


class WorkoutProgramImage(models.Model):
    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name='images')
    image_file = models.FileField(upload_to=program_image_upload_to)


class ExerciseImage(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='images')
    image_file = models.FileField(upload_to=exercise_image_upload_to)


class SessionImage(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='images')
    image_file = models.FileField(upload_to=session_image_upload_to)


class RequestStatus(Enum):
    PENDING = 'Pending'
    REJECTED = 'Rejected'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'

    @classmethod
    def choices(cls):
        return [(key, key.value) for key in cls]


class WorkoutProgramRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workout_program_requests')
    program = models.ForeignKey(WorkoutProgram, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    request_date = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=RequestStatus.choices(),  # Using Enum choices
        default=RequestStatus.PENDING
    )

    def __str__(self):
        return f"Request by {self.user.full_name} for {self.program.title if self.program else 'Unknown Program'} (Status: {self.status})"
