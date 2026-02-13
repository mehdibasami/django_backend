from rest_framework import serializers
from ..fitness.models.workout import Exercise, WorkoutProgram, WorkoutProgramRequest, WorkoutSession, WorkoutExercise, ProgramAssignment


# TODO create methods
class ExerciseWriteSerializer(serializers.ModelSerializer):

    video = serializers.FileField(
        allow_empty_file=True,
        use_url=False,
        required=False,
    )

    class Meta:
        model = Exercise
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug', 'is_verified', 'is_custom', 'is_active', 'is_public', 'handle', 'created_by']


class ExerciseReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExerciseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutExercise
        fields = [
            'id', 'session', 'exercise', 'sets', 'reps',
            'duration', 'rest_time', 'tempo'
        ]
        read_only_fields = ['id']


class WorkoutProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutProgram
        fields = [
            'id', 'title', 'slug', 'description',
            'created_by', 'assigned_to', 'created_at', 'updated_at',
            'off_percent', 'is_active', 'is_public', 'is_custom', 'is_verified',
            'price', 'duration', 'level', 'handle',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WorkoutSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutSession
        fields = [
            'id', 'program', 'day_title', 'slug', 'notes',
            'week_number', 'created_by', 'created_at', 'updated_at',
            'equipments', 'location', 'is_rest_day', 'session_type',
            'video', 'duration', 'intensity',
            'popularity', 'is_public'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserWorkoutProgramSerializer(serializers.ModelSerializer):
    program = WorkoutProgramSerializer()

    class Meta:
        model = ProgramAssignment
        fields = ['id', 'program', 'assigned_at', 'is_active', 'user']


class WorkoutProgramRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutProgramRequest
        fields = ['user', 'program', 'details', 'status', 'request_date']
        read_only_fields = ['status', 'request_date']  # These fields are read-only

    def create(self, validated_data):
        user = validated_data['user']
        program = validated_data['program']
        details = validated_data['details']
        request = WorkoutProgramRequest.objects.create(user=user, program=program, details=details)
        return request
