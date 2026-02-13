from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from apps.fitness.serializers.workout_program import (
    WorkoutProgramBuilderSerializer,
    WorkoutProgramDeepSerializer,
    WorkoutProgramSerializer
)
from apps.fitness.services.workout_program_service import WorkoutProgramService
from apps.fitness.models.workout import WorkoutProgram
from config.utils.response_state import SuccessResponse


class WorkoutProgramBuilderView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create program with sessions & exercises",
        request_body=WorkoutProgramBuilderSerializer,
        responses={201: WorkoutProgramDeepSerializer}
    )
    def post(self, request):
        serializer = WorkoutProgramBuilderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        program = WorkoutProgramService.create_program_with_sessions(request.user, serializer.validated_data)
        return SuccessResponse(WorkoutProgramDeepSerializer(program).data, status=201)

    @swagger_auto_schema(
        operation_summary="Update program with sessions & exercises",
        request_body=WorkoutProgramBuilderSerializer,
        responses={200: WorkoutProgramDeepSerializer}
    )
    def put(self, request, program_id):
        serializer = WorkoutProgramBuilderSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        program = WorkoutProgramService.update_program_with_sessions(request.user, program_id, serializer.validated_data)
        return SuccessResponse(WorkoutProgramDeepSerializer(program).data)


class WorkoutProgramListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List all programs of the user",
        responses={200: WorkoutProgramSerializer(many=True)}
    )
    def get(self, request):
        programs = WorkoutProgram.objects.filter(created_by=request.user)
        return SuccessResponse(WorkoutProgramSerializer(programs, many=True).data)


class WorkoutProgramDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve a program with sessions",
        responses={200: WorkoutProgramDeepSerializer}
    )
    def get(self, request, program_id):
        program = WorkoutProgram.objects.get(id=program_id)
        return SuccessResponse(WorkoutProgramDeepSerializer(program).data)

    @swagger_auto_schema(
        operation_summary="Delete a program",
        responses={204: "Deleted"}
    )
    def delete(self, request, program_id):
        WorkoutProgramService.delete_program(request.user, program_id)
        return SuccessResponse(status=204)


class WorkoutProgramPublishView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Publish a program",
        responses={200: WorkoutProgramDeepSerializer}
    )
    def post(self, request, program_id):
        program = WorkoutProgramService.publish_program(request.user, program_id)
        return SuccessResponse(WorkoutProgramDeepSerializer(program).data)


class WorkoutProgramCloneView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Clone program (deep clone with sessions & exercises)",
        responses={201: WorkoutProgramDeepSerializer}
    )
    def post(self, request, program_id):
        program = WorkoutProgramService.clone_program(request.user, program_id)
        return SuccessResponse(WorkoutProgramDeepSerializer(program).data, status=201)
