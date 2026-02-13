from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.fitness.models.workout import ProgramAssignment
from apps.fitness.serializers.program_assignment import ProgramAssignmentSerializer
from config.utils.pagination import StandardResultsSetPagination
from config.utils.response_state import SuccessResponse, ServerErrorResponse


class ClientAssignedProgramsView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        try:
            queryset = ProgramAssignment.objects.filter(
                client=request.user,
                is_active=True
            )

            paginator = self.pagination_class()
            paginated = paginator.paginate_queryset(queryset, request, view=self)
            serializer = ProgramAssignmentSerializer(paginated, many=True)

            return SuccessResponse(
                data=paginator.get_paginated_response(serializer.data).data
            )
        except Exception as e:
            return ServerErrorResponse(message=str(e))
