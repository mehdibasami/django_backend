# apps/fitness/views/exercise_views.py

from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from apps.fitness.serializers.exercise import ExerciseSerializer
from apps.fitness.services.exercise_service import ExerciseService
from config.utils.response_state import SuccessResponse


class ExerciseView(APIView):

    @swagger_auto_schema(
        operation_summary="List exercises",
        operation_description="List public exercises and exercises created by the user",
        responses={200: ExerciseSerializer(many=True)}
    )
    def get(self, request):
        exercises = ExerciseService.list_exercises(request.user)
        serializer = ExerciseSerializer(exercises, many=True)
        return SuccessResponse(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create exercise",
        request_body=ExerciseSerializer,
        responses={201: ExerciseSerializer}
    )
    def post(self, request):
        serializer = ExerciseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        exercise = ExerciseService.create_exercise(
            actor=request.user,
            data=serializer.validated_data
        )

        return SuccessResponse(
            ExerciseSerializer(exercise).data,
            status=201
        )


class ExerciseDetailView(APIView):

    @swagger_auto_schema(
        operation_summary="Get exercise detail",
        responses={200: ExerciseSerializer}
    )
    def get(self, request, exercise_id):
        exercise = ExerciseService.update_exercise(
            actor=request.user,
            exercise_id=exercise_id,
            data={}
        )
        return SuccessResponse(ExerciseSerializer(exercise).data)

    @swagger_auto_schema(
        operation_summary="Update exercise",
        request_body=ExerciseSerializer,
        responses={200: ExerciseSerializer}
    )
    def put(self, request, exercise_id):
        serializer = ExerciseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        exercise = ExerciseService.update_exercise(
            actor=request.user,
            exercise_id=exercise_id,
            data=serializer.validated_data
        )

        return SuccessResponse(ExerciseSerializer(exercise).data)

    @swagger_auto_schema(
        operation_summary="Delete exercise",
    )
    def delete(self, request, exercise_id):
        ExerciseService.delete_exercise(request.user, exercise_id)
        return SuccessResponse(message="Exercise deleted")
