# apps/fitness/serializers/workout_exercise.py

from rest_framework import serializers
from apps.fitness.models.workout import WorkoutExercise


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(
        source='exercise.name',
        read_only=True
    )

    class Meta:
        model = WorkoutExercise
        fields = [
            'id',
            'session',
            'exercise',
            'exercise_name',
            'sets',
            'reps',
            'duration',
            'rest_time',
            'tempo',
        ]
        read_only_fields = ['id']
