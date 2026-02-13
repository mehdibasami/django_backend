from rest_framework import serializers
from apps.fitness.models.workout import ProgramAssignment
from apps.payments.serializers.coach_service import CoachServiceRequestSerializer


class ProgramAssignmentSerializer(serializers.ModelSerializer):
    program_title = serializers.CharField(source="program.title", read_only=True)
    coach_name = serializers.CharField(source="coach.full_name", read_only=True)
    coach_service_request = CoachServiceRequestSerializer(read_only=True)

    class Meta:
        model = ProgramAssignment
        fields = [
            "id",
            "client",
            "program",
            "program_title",
            "coach",
            "coach_name",
            "coach_service_request",
            "assigned_at",
            "is_active",
        ]
        read_only_fields = ["coach", "assigned_at"]


class ProgramAssignmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a ProgramAssignment
    """
    client_id = serializers.UUIDField(write_only=True)
    program_id = serializers.UUIDField(write_only=True)
    coach_service_request_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = ProgramAssignment
        fields = [
            'client_id',
            'program_id',
            'coach_service_request_id',
        ]
