
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.renderers import JSONRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
import requests

from apps.account.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserInfoSerializer,
    GoogleSignInSerializer,
    RegisteredUserResponseSerializer
)
from config.utils.response_state import (
    SuccessResponse,
    SuccessResponse201,
    BadRequestResponse,
    ServerErrorResponse,
)
from config.utils.custom_serializers import create_response_serializer
from apps.account.models import CoachProfile, User


class RegisterView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    renderer_classes = [JSONRenderer]

    @swagger_auto_schema(
        operation_description="Register Panel",
        request_body=RegisterSerializer,
        responses={
            201: create_response_serializer(
                data_serializer_class=RegisteredUserResponseSerializer,
                text_message="Registration successful"
            )
        },
    )
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                login(request, user)
                response = {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "status": "success",
                    "user": user  # pass user instance directly
                }
                # Serialize using RegisteredUserResponseSerializer
                response_serializer = RegisteredUserResponseSerializer(response)
                return SuccessResponse201(
                    message="Registration successful",
                    data=response_serializer.data,
                )
            return BadRequestResponse(errors=serializer.errors)
        except Exception as e:
            return ServerErrorResponse(errors=str(e))


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Login Panel",
        request_body=LoginSerializer,
        responses={
            200: create_response_serializer(
                data_serializer_class=RegisteredUserResponseSerializer,
                text_message="Login successful"
            )
        },
    )
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.validated_data
                refresh = RefreshToken.for_user(user)
                login(request, user)
                response = {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "status": "success",
                    "user": user  # pass user instance directly
                    }
                # Serialize using RegisteredUserResponseSerializer
                response_serializer = RegisteredUserResponseSerializer(response)
                return SuccessResponse(
                    message="Login successful",
                    data=response_serializer.data,
                )
            return BadRequestResponse(errors=serializer.errors)
        except Exception as e:
            return ServerErrorResponse(errors=str(e))


class GoogleSignInView(APIView):
    parser_classes = [FormParser, JSONParser]
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Sign in or register with Google access token",
        request_body=GoogleSignInSerializer,
        responses={
            200: RegisteredUserResponseSerializer,
            201: RegisteredUserResponseSerializer,
            400: "Bad Request",
        },
    )
    def post(self, request):
        try:
            serializer = GoogleSignInSerializer(data=request.data)
            if not serializer.is_valid():
                return BadRequestResponse(
                    message="Invalid data",
                    errors=serializer.errors
                )

            access_token = serializer.validated_data["access_token"]
            if not access_token:
                return BadRequestResponse(message="Access token cannot be empty.")

            # Fetch user info from Google
            response = requests.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if response.status_code != 200:
                return BadRequestResponse(message="Invalid Google access token.")

            user_info = response.json()
            email = user_info.get("email")
            full_name = user_info.get("name", "")
            google_id = user_info.get("sub")
            picture_link = user_info.get("picture")

            if not email or not google_id:
                return BadRequestResponse(message="Failed to retrieve user info from Google.")

            # Optional flags for registering as coach or gym owner
            is_coach = request.data.get("is_coach", False)
            is_gym_owner = request.data.get("is_gym_owner", False)

            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "full_name": full_name,
                    "google_id": google_id,
                    "is_coach": bool(is_coach),
                    "is_gym_owner": bool(is_gym_owner),
                }
            )

            # New user setup
            if created:
                # Prevent password login until explicitly set
                user.set_unusable_password()
                user.save()

                # Create coach profile if user is coach
                if user.is_coach:
                    CoachProfile.objects.create(user=user)

                # Save profile picture from Google
                if picture_link:
                    pic_response = requests.get(picture_link)
                    if pic_response.status_code == 200:
                        temp_file = NamedTemporaryFile(delete=True)
                        temp_file.write(pic_response.content)
                        temp_file.flush()
                        user.profile_picture.save(
                            f"{user.username}_google.png",
                            File(temp_file),
                            save=True,
                        )

            # Login user
            login(request, user)
            refresh = RefreshToken.for_user(user)

            data = {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "status": "success",
                "user": UserInfoSerializer(user).data,
            }

            return SuccessResponse201(
                message="Google sign-in successful" if created else "Login successful",
                data=data
            )

        except Exception as e:
            return ServerErrorResponse(errors=str(e))
