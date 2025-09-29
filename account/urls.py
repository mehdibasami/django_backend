# account/urls.py
from django.urls import path
from .views import GoogleSignInView, RegisterView, LoginView, UserProfileView

urlpatterns = [
    # Register
    path('auth/register/',
         RegisterView.as_view(),
         name='register'),
    # Login
    path('auth/login/',
         LoginView.as_view(),
         name='login'),
    # Google Sign In
    path(
        "auth/google_sign_in/",
        GoogleSignInView.as_view(),
        name="gmail_login"
    ),

    # Profile services
    path('profile/', UserProfileView.as_view(), name='user-profile'),

]
