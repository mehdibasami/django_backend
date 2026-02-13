from .auth import (
    RegisterView,
    LoginView,
    GoogleSignInView

)
from .profile import (
    UserProfileView,
)
from .coach import (
    CoachProfileView,
    CoachListView,
)
__all__ = [
    "RegisterView",
    "LoginView",
    "UserProfileView",
    "CoachProfileView",
    "CoachListView",
    "GoogleSignInView",
]
