from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.fitness.serializers.program_assignment import ProgramAssignmentSerializer
from apps.account.permissions.workout import CanAssignWorkoutProgram
from config.utils.pagination import StandardResultsSetPagination
from config.utils.response_state import (
    SuccessResponse,
    NotFoundResponse,
    ServerErrorResponse,
    ForbiddenResponse,
    BadRequestResponse
)
from apps.fitness.services.program_assignment_service import ProgramAssignmentService
from config.utils.exceptions import (
    BadRequestException,
    NotFoundException,
    ForbiddenException,
)


class AssignWorkoutProgramView(APIView):
    permission_classes = [IsAuthenticated, CanAssignWorkoutProgram]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Assign or reactivate a workout program for a client",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["client_id", "program_id"],
            properties={
                "client_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_UUID
                ),
                "program_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_UUID
                ),
                "coach_service_request_id": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_UUID,
                    description="Paid coach service request UUID (optional)"
                ),
            },
        ),
    )
    def post(self, request):
        try:
            assignment = ProgramAssignmentService.assign_program(
                actor=request.user,
                client_id=request.data.get("client_id"),
                program_id=request.data.get("program_id"),
                coach_request_id=request.data.get("coach_service_request_id"),

            )

            return SuccessResponse(
                message="Workout program assigned successfully",
                data=ProgramAssignmentSerializer(assignment).data
            )

        except BadRequestException as e:
            return BadRequestResponse(message=str(e))
        except NotFoundException as e:
            return NotFoundResponse(message=str(e))
        except ForbiddenException as e:
            return ForbiddenResponse(message=str(e))
        except Exception as e:
            return ServerErrorResponse(message=str(e))


class UnassignWorkoutProgramView(APIView):
    permission_classes = [IsAuthenticated, CanAssignWorkoutProgram]
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Unassign a workout program from a client",
    )
    def post(self, request, pk):
        try:
            ProgramAssignmentService.unassign_program(
                actor=request.user,
                assignment_id=pk
            )

            return SuccessResponse(
                message="Workout program unassigned successfully."
            )

        except NotFoundException as e:
            return NotFoundResponse(message=str(e))
        except ForbiddenException as e:
            return ForbiddenResponse(message=str(e))
        except Exception as e:
            return ServerErrorResponse(message=str(e))


class AssignmentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get workout program assignment history for a client",
        manual_parameters=[
            openapi.Parameter(
                "client_id",
                openapi.IN_PATH,
                description="Client UUID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
                required=True,
            ),
            openapi.Parameter(
                "is_active",
                openapi.IN_QUERY,
                description="Filter by active assignments",
                type=openapi.TYPE_BOOLEAN,
            ),
            openapi.Parameter(
                "program_id",
                openapi.IN_QUERY,
                description="Filter by program UUID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
            ),
            openapi.Parameter(
                "coach_id",
                openapi.IN_QUERY,
                description="Filter by coach UUID",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Items per page",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={200: ProgramAssignmentSerializer(many=True)},
    )
    def get(self, request, client_id):
        try:
            filters = {
                "is_active": request.query_params.get("is_active"),
                "program_id": request.query_params.get("program_id"),
                "from_date": request.query_params.get("from_date"),
                "to_date": request.query_params.get("to_date"),
            }

            queryset = ProgramAssignmentService.get_assignment_history(
                actor=request.user,
                client_id=client_id,
                filters=filters,
            )

            paginator = StandardResultsSetPagination()
            page = paginator.paginate_queryset(queryset, request)

            serializer = ProgramAssignmentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except ForbiddenException as e:
            return ForbiddenResponse(message=str(e))
        except Exception as e:
            return ServerErrorResponse(message=str(e))
