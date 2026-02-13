# apps/fitness/services/exercise_service.py

from django.db.models import Q
from apps.fitness.models.workout import Exercise
from config.utils.exceptions import ForbiddenException, NotFoundException


class ExerciseService:

    @staticmethod
    def list_exercises(actor):
        return Exercise.objects.filter(
            Q(is_public=True) | Q(created_by=actor),
            is_active=True
        )

    @staticmethod
    def create_exercise(actor, data):
        if not actor.is_coach:
            raise ForbiddenException("Only coaches can create exercises")

        return Exercise.objects.create(
            created_by=actor,
            **data
        )

    @staticmethod
    def update_exercise(actor, exercise_id, data):
        try:
            exercise = Exercise.objects.get(id=exercise_id, is_active=True)
        except Exercise.DoesNotExist:
            raise NotFoundException("Exercise not found")

        if exercise.created_by != actor:
            raise ForbiddenException("You cannot edit this exercise")

        for attr, value in data.items():
            setattr(exercise, attr, value)

        exercise.save()
        return exercise

    @staticmethod
    def delete_exercise(actor, exercise_id):
        try:
            exercise = Exercise.objects.get(id=exercise_id, is_active=True)
        except Exercise.DoesNotExist:
            raise NotFoundException("Exercise not found")

        if exercise.created_by != actor:
            raise ForbiddenException("You cannot delete this exercise")

        exercise.is_active = False
        exercise.save()
