from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from django.db.models import Q


from .models import Exercise, WorkoutSession, WorkoutProgram, UserWorkoutProgram
from account.models import User, UserRole
from .serializers import ExerciseReadSerializer, ExerciseWriteSerializer, ExerciseListSerializer, WorkoutProgramRequestSerializer, WorkoutSessionSerializer, WorkoutProgramSerializer, UserWorkoutProgramSerializer
from fitness_backend.utils.pagination import StandardResultsSetPagination
from fitness_backend.utils.response_state import (
    SuccessResponse,
    SuccessResponse201,
    BadRequestResponse,
    ForbiddenResponse,
    ServerErrorResponse,
    NotFoundResponse,
)
from fitness_backend.utils.custom_serializers import create_response_serializer, create_paginated_response_serializer
from account.permissions import IsActiveUserPermission, CanAssignWorkoutProgram


class ExerciseView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUserPermission]
    pagination_class = StandardResultsSetPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [JSONRenderer]

    @swagger_auto_schema(
            operation_description="Create a new exercise",
            request_body=ExerciseWriteSerializer,
            responses={
                201: create_response_serializer(
                    data_serializer_class=ExerciseReadSerializer,
                    text_message="Exercise created successfully"
                )
            },
        )
    def post(self, request):
        try:
            serializer = ExerciseWriteSerializer(
                data=request.data, context={'request': request}
            )
            if serializer.is_valid():
                exercise = serializer.save(created_by=request.user)
                read_serializer = ExerciseReadSerializer(exercise, context={'request': request})
                return SuccessResponse201(
                    message="Exercise created successfully",
                    data=read_serializer.data,
                )
            return BadRequestResponse(
                message="Validation failed",
                errors=serializer.errors,
            )
        except Exception as e:
            return ServerErrorResponse(message=str(e))

    @swagger_auto_schema(
        operation_description="Get a paginated list of all exercises",
        manual_parameters=[
            openapi.Parameter('category', openapi.IN_QUERY, description="Filter by category", type=openapi.TYPE_STRING),
            openapi.Parameter('name', openapi.IN_QUERY, description="Filter by name", type=openapi.TYPE_STRING),
            openapi.Parameter('target_muscle_group', openapi.IN_QUERY, description="Filter by muscle group", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: create_paginated_response_serializer(
                data_serializer_class=ExerciseListSerializer,
            )
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            exercises = Exercise.objects.filter(
                Q(created_by=request.user) | Q(is_public=True)
            )

            # Optional filtering
            category = request.query_params.get('category')
            name = request.query_params.get('name')
            target_muscle_group = request.query_params.get('target_muscle_group')

            if category:
                exercises = exercises.filter(translations__category__iexact=category)
            if name:
                exercises = exercises.filter(translations__name__icontains=name)
            if target_muscle_group:
                exercises = exercises.filter(translations__target_muscle_group__icontains=target_muscle_group)

            # Pagination
            paginator = self.pagination_class()
            paginated_exercises = paginator.paginate_queryset(exercises, request, view=self)
            serializer = ExerciseListSerializer(paginated_exercises, many=True)

            return SuccessResponse(data=paginator.get_paginated_response(serializer.data).data,)
        except Exception as e:
            return ServerErrorResponse(message=str(e))


class ExerciseDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [JSONRenderer]
    permission_classes = [IsAuthenticated, IsActiveUserPermission]

    @swagger_auto_schema(
        operation_description="Retrieve a specific exercise by ID",
        responses={
            200: create_response_serializer(
                data_serializer_class=ExerciseReadSerializer,
                text_message="Exercise retrieved successfully"
            ),
        },
    )
    def get(self, request, exercise_id):
        try:
            exercise = Exercise.objects.get(pk=exercise_id)
            serializer = ExerciseReadSerializer(exercise, context={'request': request})
            return SuccessResponse(
                message="Exercise retrieved successfully",
                data=serializer.data,
            )
        except Exercise.DoesNotExist:
            return NotFoundResponse(message="Exercise not found.")
        except Exception as e:
            return ServerErrorResponse(message=str(e))

    @swagger_auto_schema(
        operation_description="Partially update a specific exercise",
        request_body=ExerciseWriteSerializer,
        responses={
            200: create_response_serializer(
                data_serializer_class=ExerciseReadSerializer,
                text_message="Exercise updated successfully"
            )
        },
    )
    def patch(self, request, exercise_id):
        try:
            exercise = Exercise.objects.get(pk=exercise_id)
            if exercise.created_by != request.user:
                return ForbiddenResponse(message="You do not have permission to edit this exercise.")
            serializer = ExerciseWriteSerializer(
                exercise, data=request.data, partial=True, context={'request': request}
            )
            if serializer.is_valid():
                updated_exercise = serializer.save()
                read_serializer = ExerciseReadSerializer(updated_exercise, context={'request': request})
                return SuccessResponse(
                    message="Exercise updated successfully",
                    data=read_serializer.data,
                )
            return BadRequestResponse(
                message="Validation failed",
                errors=serializer.errors,
            )
        except Exercise.DoesNotExist:
            return NotFoundResponse(message="Exercise not found.")
        except Exception as e:
            return ServerErrorResponse(message=str(e))

    @swagger_auto_schema(
        operation_description="Delete a specific exercise",
        responses={
            204: create_response_serializer(
                    text_message="Exercise deleted successfully"
                )
        },
    )
    def delete(self, request, exercise_id):
        try:
            exercise = Exercise.objects.get(pk=exercise_id)
            if exercise.created_by != request.user:
                return ForbiddenResponse(message="You do not have permission to delete this exercise.")
            exercise.delete()
            return SuccessResponse(
                message="Exercise deleted successfully",
                data=None,
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exercise.DoesNotExist:
            return NotFoundResponse(message="Exercise not found.")
        except Exception as e:
            return ServerErrorResponse(message=str(e))


# Workout Session View
class WorkoutSessionView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUserPermission]
    pagination_class = StandardResultsSetPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [JSONRenderer]

    @swagger_auto_schema(
        operation_description="Create a new workout session",
        request_body=WorkoutSessionSerializer,
        responses={
            201: create_response_serializer(
                data_serializer_class=WorkoutSessionSerializer,
                text_message="Workout session created successfully"
            )
        },
    )
    def post(self, request):
        try:
            serializer = WorkoutSessionSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                session = serializer.save(created_by=request.user)
                read_serializer = WorkoutSessionSerializer(session, context={"request": request})
                return SuccessResponse201(
                    message="Workout session created successfully",
                    data=read_serializer.data,
                )
            return BadRequestResponse(
                message="Validation failed",
                errors=serializer.errors,
            )
        except Exception as e:
            return ServerErrorResponse(message=str(e))

    # @swagger_auto_schema(
    #     operation_description="Get a paginated list of workout sessions",
    #     manual_parameters=[
    #         openapi.Parameter("page", openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
    #         openapi.Parameter("page_size", openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
    #         openapi.Parameter("is_rest_day", openapi.IN_QUERY, description="Filter by rest day (true/false)", type=openapi.TYPE_BOOLEAN),
    #         openapi.Parameter("location", openapi.IN_QUERY, description="Filter by location", type=openapi.TYPE_STRING),
    #     ],
    #     responses={
    #         200: create_paginated_response_serializer(
    #             data_serializer_class=WorkoutSessionSerializer,
    #             text_message="Workout sessions retrieved successfully",
    #         )
    #     },
    # )
    # def get(self, request):
    #     try:
    #         sessions = WorkoutSession.objects.all().order_by("-created_at")

    #         # Filtering example (optional)
    #         is_rest_day = request.query_params.get("is_rest_day")
    #         location = request.query_params.get("location")

    #         if is_rest_day is not None:
    #             if is_rest_day.lower() == "true":
    #                 sessions = sessions.filter(is_rest_day=True)
    #             elif is_rest_day.lower() == "false":
    #                 sessions = sessions.filter(is_rest_day=False)

    #         if location:
    #             sessions = sessions.filter(location__icontains=location)

    #         paginator = self.pagination_class()
    #         paginated_sessions = paginator.paginate_queryset(sessions, request, view=self)
    #         serializer = WorkoutSessionSerializer(paginated_sessions, many=True, context={"request": request})

    #         return SuccessResponse(data=paginator.get_paginated_response(serializer.data).data)
    #     except Exception as e:
    #         return ServerErrorResponse(message=str(e))


class WorkoutSessionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUserPermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [JSONRenderer]

    def get(self, request, session_id):
        try:

            session = WorkoutSession.objects.get(pk=session_id)
            # check if user is assigned to the session or the session is public
            if (session.created_by != request.user):
                return ForbiddenResponse(message="You do not have permission to view this workout session.")
            serializer = WorkoutSessionSerializer(session, context={"request": request})
            return SuccessResponse(
                message="Workout session retrieved successfully",
                data=serializer.data,
            )
        except WorkoutSession.DoesNotExist:
            return NotFoundResponse(message="Workout session not found.")
        except Exception as e:
            return ServerErrorResponse(message=str(e))

    @swagger_auto_schema(
        operation_description="Update a workout session completely",
        request_body=WorkoutSessionSerializer,
        responses={
            200: create_response_serializer(
                data_serializer_class=WorkoutSessionSerializer,
                text_message="Workout session updated successfully"
            )
        },
    )
    def put(self, request, session_id):
        try:
            session = WorkoutSession.objects.get(pk=session_id)
            if session.created_by != request.user:
                return ForbiddenResponse(message="You do not have permission to update this workout session.")
            serializer = WorkoutSessionSerializer(session, data=request.data, partial=False, context={"request": request})
            if serializer.is_valid():
                updated_session = serializer.save()
                read_serializer = WorkoutSessionSerializer(updated_session, context={"request": request})
                return SuccessResponse(
                    message="Workout session updated successfully",
                    data=read_serializer.data,
                )
            return BadRequestResponse(
                message="Validation failed",
                errors=serializer.errors,
            )
        except WorkoutSession.DoesNotExist:
            return NotFoundResponse(message="Workout session not found.")
        except Exception as e:
            return ServerErrorResponse(message=str(e))

    @swagger_auto_schema(
        operation_description="Partially update a workout session",
        request_body=WorkoutSessionSerializer,
        responses={
            200: create_response_serializer(
                data_serializer_class=WorkoutSessionSerializer,
                text_message="Workout session updated successfully"
            )
        },
    )
    def patch(self, request, session_id):
        try:
            session = WorkoutSession.objects.get(pk=session_id)
            if session.created_by != request.user:
                return ForbiddenResponse(message="You do not have permission to update this workout session.")
            serializer = WorkoutSessionSerializer(session, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                updated_session = serializer.save()
                read_serializer = WorkoutSessionSerializer(updated_session, context={"request": request})
                return SuccessResponse(
                    message="Workout session updated successfully",
                    data=read_serializer.data,
                )
            return BadRequestResponse(
                message="Validation failed",
                errors=serializer.errors,
            )
        except WorkoutSession.DoesNotExist:
            return NotFoundResponse(message="Workout session not found.")
        except Exception as e:
            return ServerErrorResponse(message=str(e))

    @swagger_auto_schema(
        operation_description="Delete a workout session",
        responses={
            204: create_response_serializer(text_message="Workout session deleted successfully")
        },
    )
    def delete(self, request, session_id):
        try:
            session = WorkoutSession.objects.get(pk=session_id)
            if session.created_by != request.user:
                return ForbiddenResponse(message="You do not have permission to delete this workout session.")
            session.delete()
            return SuccessResponse(
                message="Workout session deleted successfully",
                data=None,
                status_code=status.HTTP_204_NO_CONTENT,
            )
        except WorkoutSession.DoesNotExist:
            return NotFoundResponse(message="Workout session not found.")
        except Exception as e:
            return ServerErrorResponse(message=str(e))


# workout program view
class WorkoutProgramView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUserPermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [JSONRenderer]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        operation_description="Create a new workout program (plan)",
        request_body=WorkoutProgramSerializer,
        responses={
            201: create_response_serializer(
                data_serializer_class=WorkoutProgramSerializer,
                text_message="Workout program created successfully"
            )
        }
    )
    def post(self, request):
        try:
            allowed_roles = {
                UserRole.personal_trainer.value,
                UserRole.sports_coach.value,
                UserRole.health_professional.value,
            }
            # Assume user.role is stored as a string, e.g. 'Personal trainer'
            user_role = request.user.role  # Convert to enum
            if user_role not in allowed_roles:
                return BadRequestResponse(message="You do not have permission to create workout programs.",)
            serializer = WorkoutProgramSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                program = serializer.save(created_by=request.user)
                return SuccessResponse201(
                    message="Workout program created successfully",
                    data=WorkoutProgramSerializer(program, context={'request': request}).data
                )
            return BadRequestResponse(message="Validation failed", errors=serializer.errors)
        except Exception as e:
            return ServerErrorResponse(message=str(e))

    @swagger_auto_schema(
        operation_description="List all workout programs",
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter("page_size", openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
            openapi.Parameter("level", openapi.IN_QUERY, description="Filter by level", type=openapi.TYPE_STRING),
        ],
        responses={
            200: create_paginated_response_serializer(
                data_serializer_class=WorkoutProgramSerializer,
            )
        },
    )
    def get(self, request):
        try:
            programs = WorkoutProgram.objects.all()

            level = request.query_params.get("level")
            if level:
                programs = programs.filter(level__iexact=level)

            paginator = self.pagination_class()
            paginated = paginator.paginate_queryset(programs, request, view=self)
            serializer = WorkoutProgramSerializer(paginated, many=True, context={"request": request})
            return SuccessResponse(data=paginator.get_paginated_response(serializer.data).data)
        except Exception as e:
            return ServerErrorResponse(message=str(e))


# assuming the workout program to user
class AssignWorkoutProgramView(APIView):
    permission_classes = [IsAuthenticated, IsActiveUserPermission]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        operation_description="Assign a workout program to a user (recorded assignment)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["program_id", "user_id"],
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='ID of the user'),
                "program_id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, description='ID of the workout program'),
            },
        ),
        responses={
            200: create_response_serializer(text_message="Workout plan assigned successfully", data_serializer_class=UserWorkoutProgramSerializer),
            400: create_response_serializer(text_message="Bad request"),
        },
    )
    def post(self, request):
        try:
            rolePermission = CanAssignWorkoutProgram()
            if not rolePermission.has_permission(request, self):
                return ForbiddenResponse(message="You do not have permission to assign workout programs.")
            user_id = request.data.get('user_id')
            program_id = request.data.get("program_id")
            if not user_id or not program_id:
                return BadRequestResponse(message="Both user_id and program_id are required.")
            user = User.objects.get(id=user_id)
            program = WorkoutProgram.objects.get(pk=program_id)
            # Assign new
            assignment, created = UserWorkoutProgram.objects.update_or_create(
                user=user,
                program=program,
            )
            data = UserWorkoutProgramSerializer(assignment, context={"request": request}).data

            return SuccessResponse(
                message="Workout plan assigned successfully",
                data=data
            )
        except WorkoutProgram.DoesNotExist:
            return NotFoundResponse(message="Workout program not found.")
        except User.DoesNotExist:
            return NotFoundResponse(message="User not found.")
        except Exception as e:
            return ServerErrorResponse(message=str(e))

    @swagger_auto_schema(
        operation_description="Get a list of all workout plans ever assigned to the current user",
        responses={
            200: create_paginated_response_serializer(
                data_serializer_class=UserWorkoutProgramSerializer,
                # text_message="Assigned workout plans retrieved successfully"
            )
        }
    )
    def get(self, request):
        try:
            queryset = UserWorkoutProgram.objects.filter(user=request.user)
            paginator = self.pagination_class()
            paginated = paginator.paginate_queryset(queryset, request, view=self)
            serializer = UserWorkoutProgramSerializer(paginated, many=True, context={"request": request})
            return SuccessResponse(data=paginator.get_paginated_response(serializer.data).data)
        except Exception as e:
            return ServerErrorResponse(message=str(e))


class SubmitWorkoutProgramRequestView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [JSONRenderer]

    @swagger_auto_schema(
        operation_description="Submit a request for a workout program.",
        request_body=WorkoutProgramRequestSerializer,
        responses={
            201: create_response_serializer(
                data_serializer_class=WorkoutProgramRequestSerializer,
                text_message="Workout program request submitted successfully"
            ),
            400: "Bad Request"
        }
    )
    def post(self, request):
        try:
            program_id = request.data.get('program')  # Fetch the program ID from the request
            program = None

            if program_id:
                try:
                    program = WorkoutProgram.objects.get(id=program_id)
                except WorkoutProgram.DoesNotExist:
                    return BadRequestResponse(message="Program not found.")

            # Validate the input data through the serializer
            serializer = WorkoutProgramRequestSerializer(data=request.data)
            if serializer.is_valid():
                if not program:
                    return BadRequestResponse(message="Program must be provided.")

                # Save the request, linking it to the current user and program
                request_instance = serializer.save(user=request.user, program=program)
                return SuccessResponse201(
                    message="Workout program request submitted successfully",
                    data=WorkoutProgramRequestSerializer(request_instance).data,
                )

            return BadRequestResponse(
                message="Validation failed",
                errors=serializer.errors,
            )

        except Exception as e:
            return ServerErrorResponse(errors=str(e))
