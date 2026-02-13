# apps/fitness/views/workout_exercise_views.py

from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from apps.fitness.serializers.workout_exercise import WorkoutExerciseSerializer
from apps.fitness.services.workout_exercise_service import WorkoutExerciseService
from config.utils.response_state import SuccessResponse


class WorkoutExerciseView(APIView):

    @swagger_auto_schema(
        operation_summary="Add exercise to session",
        request_body=WorkoutExerciseSerializer,
        responses={201: WorkoutExerciseSerializer}
    )
    def post(self, request):
        serializer = WorkoutExerciseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workout_exercise = WorkoutExerciseService.add_exercise(
            actor=request.user,
            data=serializer.validated_data
        )

        return SuccessResponse(
            WorkoutExerciseSerializer(workout_exercise).data,
            status=201
        )


class WorkoutExerciseDetailView(APIView):

    @swagger_auto_schema(
        operation_summary="Update workout exercise",
        request_body=WorkoutExerciseSerializer,
        responses={200: WorkoutExerciseSerializer}
    )
    def put(self, request, workout_exercise_id):
        serializer = WorkoutExerciseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        workout_exercise = WorkoutExerciseService.update_exercise(
            actor=request.user,
            workout_exercise_id=workout_exercise_id,
            data=serializer.validated_data
        )

        return SuccessResponse(
            WorkoutExerciseSerializer(workout_exercise).data
        )

    @swagger_auto_schema(
        operation_summary="Remove exercise from session"
    )
    def delete(self, request, workout_exercise_id):
        WorkoutExerciseService.delete_exercise(
            actor=request.user,
            workout_exercise_id=workout_exercise_id
        )
        return SuccessResponse(message="Exercise removed from session")
