from django.urls import path
from apps.account.views import RegisterView, LoginView, GoogleSignInView, UserProfileView, CoachProfileView, CoachListView


urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/google-signin/', GoogleSignInView.as_view(), name='google-signin'),

    # Profile
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    # Coach
    path('coaches/', CoachListView.as_view(), name='coach-list'),
    path('coaches/profile/<uuid:coach_id>/', CoachProfileView.as_view(), name='coach-profile'),  # For viewing/updating own profile
]
