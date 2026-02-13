# apps/fitness/services/workout_exercise_service.py

from apps.fitness.models.workout import WorkoutExercise, WorkoutSession
from config.utils.exceptions import NotFoundException, ForbiddenException


class WorkoutExerciseService:

    @staticmethod
    def add_exercise(actor, data):
        session = WorkoutSession.objects.filter(id=data['session'].id).first()
        if not session:
            raise NotFoundException("Session not found")

        if session.created_by != actor:
            raise ForbiddenException("You cannot modify this session")

        return WorkoutExercise.objects.create(**data)

    @staticmethod
    def update_exercise(actor, workout_exercise_id, data):
        try:
            we = WorkoutExercise.objects.select_related('session').get(id=workout_exercise_id)
        except WorkoutExercise.DoesNotExist:
            raise NotFoundException("Workout exercise not found")

        if we.session.created_by != actor:
            raise ForbiddenException("You cannot modify this session")

        for attr, value in data.items():
            setattr(we, attr, value)

        we.save()
        return we

    @staticmethod
    def delete_exercise(actor, workout_exercise_id):
        try:
            we = WorkoutExercise.objects.select_related('session').get(id=workout_exercise_id)
        except WorkoutExercise.DoesNotExist:
            raise NotFoundException("Workout exercise not found")

        if we.session.created_by != actor:
            raise ForbiddenException("You cannot modify this session")

        we.delete()
