from rest_framework import serializers
from apps.fitness.models.workout import WorkoutSession


class ClientWorkoutSessionSerializer(serializers.ModelSerializer):
    program_title = serializers.CharField(source="program.title", read_only=True)

    class Meta:
        model = WorkoutSession
        fields = [
            "id",
            "title",
            "program",
            "program_title",
            "week_number",
            "duration",
            "intensity",
            "is_rest_day",
        ]
