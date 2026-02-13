# Program
#  └── WorkoutSessions
#       └── WorkoutExercises
#            └── Exercise

# •	Exercise = library
# •	WorkoutExercise = how that exercise is performed in this session

from django.db import models
from uuid import uuid4
from django.utils.text import slugify
from django.conf import settings
from apps.fitness.enums import RequestStatus
from apps.payments.models.coach_service import CoachServiceRequest
User = settings.AUTH_USER_MODEL


def exercise_image_upload_to(instance, filename):

    uid = instance.exercise.created_by.id or "system"
    exercise_id = instance.exercise.id
    return f'users/{uid}/workout/exercises/{exercise_id}/images/{filename}'


def exercise_video_upload_to(instance, filename):
    uid = instance.exercise.created_by.id or "system"
    exercise_id = instance.exercise.id
    return f'users/{uid}/workout/exercises/{exercise_id}/videos/{filename}'


def program_image_upload_to(instance, filename):

    uid = instance.program.created_by.id or "system"
    program_id = instance.program.id
    return f'users/{uid}/workout/programs/{program_id}/images/{filename}'


def program_video_upload_to(instance, filename):
    program_id = instance.id
    uid = instance.created_by.id or "system"
    return f'users/{uid}/workout/programs/{program_id}/videos/{filename}'


def session_image_upload_to(instance, filename):

    uid = instance.session.created_by.id or "system"
    session_id = instance.session.id
    return f'users/{uid}/workout/sessions/{session_id}/images/{filename}'


def session_video_upload_to(instance, filename):
    session_id = instance.id
    uid = instance.created_by.id or "system"
    return f'users/{uid}/workout/sessions/{session_id}/videos/{filename}'


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


# --------------------------------
# Exercise Models

class Exercise(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True, default='')
    slug = models.SlugField(max_length=255, blank=True, db_index=True)
    instructions = models.JSONField(default=list)
    # self-referential alternatives
    alternatives = models.ManyToManyField(
        'self',
        blank=True,
        # symmetrical=True,
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


class ExerciseImage(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='images')
    image_file = models.FileField(upload_to=exercise_image_upload_to)


class ExerciseVideo(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='videos')
    video_file = models.FileField(upload_to=exercise_video_upload_to)


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


# --------------------------------
# Workout Program Models

class WorkoutProgram(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, default='')
    slug = models.SlugField(max_length=255, blank=True, db_index=True)

    description = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_programs', null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    off_percent = models.FloatField(default=0.0)
    duration = models.CharField(max_length=50, blank=True)
    level = models.CharField(max_length=50, blank=True)
    goal = models.CharField(max_length=100, blank=True)
    duration_weeks = models.PositiveIntegerField(default=4)

    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    video = models.FileField(upload_to=program_video_upload_to, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    equipment = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class WorkoutProgramImage(models.Model):
    program = models.ForeignKey(WorkoutProgram, on_delete=models.CASCADE, related_name='images')
    image_file = models.FileField(upload_to=program_image_upload_to)


class ProgramAssignment(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_programs'
    )
    program = models.ForeignKey(
        WorkoutProgram,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    coach = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='program_assignments'
    )
    coach_service_request = models.OneToOneField(   # 🔒 one request → one assignment
        CoachServiceRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='program_assignment'
    )

    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-assigned_at']
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'program'],
                condition=models.Q(is_active=True),
                name='unique_active_program_assignment'
            )
        ]

    def __str__(self):
        return f"{self.client} → {self.program}"


class WorkoutSession(models.Model):
    class Meta:
        ordering = ['week_number', 'created_at']

    @property
    def all_images(self):
        """Returns all images associated with this project."""
        return self.images.all()

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    slug = models.SlugField(max_length=255, blank=True, db_index=True)
    program = models.ForeignKey(WorkoutProgram, on_delete=models.SET_NULL, related_name='sessions', null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_sessions', null=True)

    title = models.CharField(max_length=100, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    week_number = models.PositiveIntegerField(default=1)
    equipments = models.CharField(max_length=255, blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    session_type = models.CharField(max_length=100, blank=True)
    duration = models.CharField(max_length=50, blank=True)
    intensity = models.CharField(max_length=50, blank=True)
    popularity = models.PositiveIntegerField(default=0)
    video = models.FileField(upload_to=session_video_upload_to, blank=True, null=True)

    is_public = models.BooleanField(default=False)
    is_rest_day = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.program.title if self.program else 'No Program'}"


class SessionImage(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name='images')
    image_file = models.FileField(upload_to=session_image_upload_to)


class WorkoutExercise(models.Model):
    class Meta:
        ordering = ['id']

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


class WorkoutProgramRequest(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='program_requests'
    )
    program = models.ForeignKey(
        WorkoutProgram,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices(),
        default=RequestStatus.PENDING.name
    )
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.client.full_name} for {self.program.title if self.program else 'Unknown Program'} (Status: {self.status})"
