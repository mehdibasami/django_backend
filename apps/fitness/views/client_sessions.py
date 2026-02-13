from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.fitness.models.workout import WorkoutSession, ProgramAssignment
from apps.fitness.serializers.client_sessions import ClientWorkoutSessionSerializer
from config.utils.response_state import SuccessResponse, ServerErrorResponse


class ClientWorkoutSessionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            assigned_programs = ProgramAssignment.objects.filter(
                client=request.user,
                is_active=True
            ).values_list("program_id", flat=True)

            sessions = WorkoutSession.objects.filter(
                program_id__in=assigned_programs
            )

            serializer = ClientWorkoutSessionSerializer(sessions, many=True)
            return SuccessResponse(data=serializer.data)

        except Exception as e:
            return ServerErrorResponse(message=str(e))
