from rest_framework import serializers
from apps.fitness.models.workout import WorkoutProgram, WorkoutSession, WorkoutExercise, Exercise
from apps.fitness.serializers.workout_session import WorkoutSessionDeepSerializer


# Serializer to handle exercises inside a session during program creation/update
class WorkoutExerciseCreateSerializer(serializers.ModelSerializer):
    exercise_id = serializers.PrimaryKeyRelatedField(
        source='exercise',
        queryset=Exercise.objects.all(),  # Can be dynamically set in service if needed
        write_only=True
    )

    class Meta:
        model = WorkoutExercise
        fields = ['exercise_id', 'sets', 'reps', 'duration', 'rest_time', 'tempo']


# Serializer to handle sessions inside a program during creation/update
class WorkoutSessionCreateSerializer(serializers.ModelSerializer):
    exercises = WorkoutExerciseCreateSerializer(many=True)

    class Meta:
        model = WorkoutSession
        fields = [
            'title', 'notes', 'week_number', 'session_type',
            'duration', 'intensity', 'is_rest_day', 'exercises'
        ]


# Serializer for creating/updating a full program with sessions & exercises
class WorkoutProgramBuilderSerializer(serializers.ModelSerializer):
    sessions = WorkoutSessionCreateSerializer(many=True)

    class Meta:
        model = WorkoutProgram
        fields = [
            'title', 'description', 'level', 'goal', 'duration',
            'price', 'off_percent', 'is_active', 'is_public',
            'is_custom', 'is_verified', 'video', 'location', 'equipment',
            'sessions'
        ]


# Deep serializer for returning a full program with sessions & exercises
class WorkoutProgramDeepSerializer(serializers.ModelSerializer):
    sessions = WorkoutSessionDeepSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutProgram
        fields = [
            'id', 'title', 'description', 'level', 'goal', 'duration',
            'price', 'off_percent', 'is_active', 'is_public', 'is_custom',
            'is_verified', 'video', 'location', 'equipment', 'created_by',
            'sessions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sessions', 'created_at', 'updated_at', 'created_by']


# Simple serializer for listing programs without sessions
class WorkoutProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutProgram
        fields = [
            'id', 'title', 'description', 'level', 'goal',
            'duration', 'is_public', 'is_active', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
