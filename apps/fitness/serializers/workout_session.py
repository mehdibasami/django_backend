from rest_framework import serializers
from apps.fitness.models.workout import WorkoutSession, WorkoutExercise
from apps.fitness.serializers.exercise import ExerciseSerializer


# Serializer for exercises inside a session (deep view)
class WorkoutExerciseDeepSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = WorkoutExercise
        fields = [
            'id',
            'exercise',
            'sets',
            'reps',
            'duration',
            'rest_time',
            'tempo',
        ]
        read_only_fields = ['id', 'exercise']


# Deep serializer for a workout session with all exercises
class WorkoutSessionDeepSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseDeepSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutSession
        fields = [
            'id',
            'title',
            'notes',
            'week_number',
            'session_type',
            'duration',
            'intensity',
            'is_rest_day',
            'exercises',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'exercises', 'created_at', 'updated_at', 'created_by']


class WorkoutSessionSerializer(serializers.ModelSerializer):
    program_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = WorkoutSession
        fields = [
            'id',
            'program_id',
            'program',
            'title',
            'notes',
            'week_number',
            'equipments',
            'location',
            'session_type',
            'duration',
            'intensity',
            'is_public',
            'is_rest_day',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'program',
            'created_at',
            'updated_at',
        ]

    def validate_week_number(self, value):
        if value < 1:
            raise serializers.ValidationError("Week number must be >= 1.")
        return value
