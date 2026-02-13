from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.fitness.serializers.workout_session import WorkoutSessionSerializer
from apps.fitness.services.workout_session_service import WorkoutSessionService
from config.utils.response_state import SuccessResponse


class WorkoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List workout sessions",
        manual_parameters=[
            openapi.Parameter(
                'program_id',
                openapi.IN_QUERY,
                description="Filter by program",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID
            )
        ],
        responses={200: WorkoutSessionSerializer(many=True)}
    )
    def get(self, request):
        program_id = request.query_params.get('program_id')
        sessions = WorkoutSessionService.list_sessions(
            actor=request.user,
            program_id=program_id
        )
        return SuccessResponse(
            WorkoutSessionSerializer(sessions, many=True).data
        )

    @swagger_auto_schema(
        operation_summary="Create workout session",
        request_body=WorkoutSessionSerializer,
        responses={201: WorkoutSessionSerializer}
    )
    def post(self, request):
        serializer = WorkoutSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = WorkoutSessionService.create_session(
            actor=request.user,
            data=serializer.validated_data
        )

        return SuccessResponse(
            WorkoutSessionSerializer(session).data,
            status=201
        )


class WorkoutSessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve workout session",
        responses={200: WorkoutSessionSerializer}
    )
    def get(self, request, session_id):
        session = WorkoutSessionService.get_session(
            actor=request.user,
            session_id=session_id
        )
        return SuccessResponse(
            WorkoutSessionSerializer(session).data
        )

    @swagger_auto_schema(
        operation_summary="Update workout session",
        request_body=WorkoutSessionSerializer,
        responses={200: WorkoutSessionSerializer}
    )
    def put(self, request, session_id):
        serializer = WorkoutSessionSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        session = WorkoutSessionService.update_session(
            actor=request.user,
            session_id=session_id,
            data=serializer.validated_data
        )

        return SuccessResponse(
            WorkoutSessionSerializer(session).data
        )

    @swagger_auto_schema(
        operation_summary="Delete workout session",
        responses={204: "Deleted"}
    )
    def delete(self, request, session_id):
        WorkoutSessionService.delete_session(
            actor=request.user,
            session_id=session_id
        )
        return SuccessResponse(status=204)
