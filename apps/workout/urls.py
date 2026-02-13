from django.urls import path
from .views import (
    ExerciseView,
    ExerciseDetailView,
    WorkoutSessionView,
    WorkoutSessionDetailView,
    WorkoutProgramView,
    AssignWorkoutProgramView,
)

urlpatterns = [
    # Exercise endpoints
    path('workout/exercises/', ExerciseView.as_view(), name='exercise-list-create'),
    path('workout/exercises/<uuid:exercise_id>/', ExerciseDetailView.as_view(), name='exercise-detail'),

    # Workout session endpoints
    path('workout/sessions/', WorkoutSessionView.as_view(), name='workout-session-create'),
    path('workout/sessions/<uuid:session_id>/', WorkoutSessionDetailView.as_view(), name='workout-session-detail'),

    # Workout program endpoints
    path('workout/programs/', WorkoutProgramView.as_view(), name='workout-program-list-create'),
    path('workout/programs/assign/', AssignWorkoutProgramView.as_view(), name='assign-workout-program'),
]
