from django.urls import path

from apps.fitness.views.coach_clients import (
    CoachClientListCreateView,
    CoachClientDeleteView,
)
from apps.fitness.views.exercise import ExerciseDetailView, ExerciseView
from apps.fitness.views.program_assignments import (
    AssignWorkoutProgramView,
    UnassignWorkoutProgramView,
    AssignmentHistoryView,
)
from apps.fitness.views.client_coaches import ClientCoachListView
from apps.fitness.views.client_programs import ClientAssignedProgramsView
from apps.fitness.views.client_sessions import ClientWorkoutSessionsView
from apps.fitness.views.workout_exercise import WorkoutExerciseDetailView, WorkoutExerciseView
from apps.fitness.views.workout_program import WorkoutProgramBuilderView, WorkoutProgramDetailView, WorkoutProgramListView, WorkoutProgramCloneView, WorkoutProgramPublishView
from apps.fitness.views.workout_session import WorkoutSessionDetailView, WorkoutSessionView

urlpatterns = [
    # ---------------- COACH ----------------
    # Manage clients
    path('coach/clients/', CoachClientListCreateView.as_view(), name='coach-client-list-create'),
    path('coach/clients/<uuid:pk>/', CoachClientDeleteView.as_view(), name='coach-client-delete'),

    # Program assignments
    path('coach/assign-program/', AssignWorkoutProgramView.as_view(), name='assign-workout-program'),
    path('coach/unassign-program/<uuid:pk>/', UnassignWorkoutProgramView.as_view(), name='unassign-workout-program'),

    # Client assignment history
    path('coach/assignment-history/<uuid:client_id>/', AssignmentHistoryView.as_view(), name='assignment-history'),

    # ---------------- CLIENT ----------------
    path('client/coaches/', ClientCoachListView.as_view(), name='client-coach-list'),
    path('client/programs/', ClientAssignedProgramsView.as_view(), name='client-programs'),
    path('client/sessions/', ClientWorkoutSessionsView.as_view(), name='client-sessions'),
    # ---------------- WORKOUTS ----------------
    # Exercise
    path('workouts/exercises/', ExerciseView.as_view()),
    path('workouts/exercises/<uuid:pk>/', ExerciseDetailView.as_view()),
    # Workout Exercises
    path('workouts/workout-exercises/', WorkoutExerciseView.as_view()),
    path('workouts/workout-exercises/<uuid:workout_exercise_id>/', WorkoutExerciseDetailView.as_view()),
    # Workout Sessions
    path('workouts/sessions/', WorkoutSessionView.as_view()),
    path('workouts/sessions/<uuid:session_id>/', WorkoutSessionDetailView.as_view()),
    # Workout Programs
    # Program builder (create/update)
    path('workouts/programs/builder/', WorkoutProgramBuilderView.as_view(), name='program-builder-create'),
    path('workouts/programs/builder/<uuid:program_id>/', WorkoutProgramBuilderView.as_view(), name='program-builder-update'),

    # List programs
    path('workouts/programs/', WorkoutProgramListView.as_view(), name='program-list'),

    # Detail, delete
    path('workouts/programs/<uuid:program_id>/', WorkoutProgramDetailView.as_view(), name='program-detail'),

    # Publish program
    path('workouts/programs/<uuid:program_id>/publish/', WorkoutProgramPublishView.as_view(), name='program-publish'),

    # Clone program
    path('workouts/programs/<uuid:program_id>/clone/', WorkoutProgramCloneView.as_view(), name='program-clone'),

]
