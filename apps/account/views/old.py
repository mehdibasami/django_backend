# from django.core.files.temp import NamedTemporaryFile
# from django.core.files import File
# from rest_framework import status

# from rest_framework.views import APIView
# from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
# from rest_framework.renderers import JSONRenderer
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth import login
# from apps.account.models import User
# from apps.account.serializers.serializers import GoogleSignInSerializer, RegisterSerializer, RegisteredUserSerializer, LoginSerializer, UserInfoSerializer, UserProfileUpdateSerializer
# from config.utils.custom_serializers import create_response_serializer
# from config.utils.response_state import SuccessResponse, BadRequestResponse, ServerErrorResponse, SuccessResponse201
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework import permissions
# from rest_framework.permissions import IsAuthenticated
# import requests


# # Account views here.


# # Register View
# class RegisterView(APIView):
#     parser_classes = [FormParser, MultiPartParser, JSONParser]
#     renderer_classes = [JSONRenderer]
#     permission_classes = [permissions.AllowAny]

#     # POST
#     @swagger_auto_schema(
#         operation_description="Register Panel",
#         request_body=RegisterSerializer,
#         responses={
#             201: create_response_serializer(
#                 data_serializer_class=RegisteredUserSerializer,
#                 text_message="Registration successful"
#             )
#         },
#     )
#     def post(self, request):
#         try:

#             serializer = RegisterSerializer(data=request.data)
#             if serializer.is_valid():
#                 user = serializer.save()
#                 refresh = RefreshToken.for_user(user)
#                 login(request, user)
#                 data = {
#                     "access_token": str(refresh.access_token),
#                     "refresh_token": str(refresh),
#                     "status": "success",
#                     "user": UserInfoSerializer(user).data
#                 }
#                 return SuccessResponse201(
#                     message="Registration successful",
#                     data=data,
#                 )
#             else:
#                 return BadRequestResponse(
#                     message="Registration failed",
#                     errors=serializer.errors
#                 )
#         except Exception as e:
#             return ServerErrorResponse(
#                 errors=str(e),
#             )


# class LoginView(APIView):
#     parser_classes = [FormParser, MultiPartParser, JSONParser]
#     renderer_classes = [JSONRenderer]
#     permission_classes = [permissions.AllowAny]

#     # POST
#     @swagger_auto_schema(
#         operation_description="Login Panel",
#         request_body=LoginSerializer,
#         responses={
#             200: create_response_serializer(
#                 data_serializer_class=RegisteredUserSerializer,
#                 text_message="Login successful"
#             )
#         },
#     )
#     def post(self, request):
#         try:
#             serializer = LoginSerializer(data=request.data)
#             if serializer.is_valid():
#                 user = serializer.validated_data
#                 refresh = RefreshToken.for_user(user)
#                 login(request, user)
#                 data = {
#                         "access_token": str(refresh.access_token),
#                         "refresh_token": str(refresh),
#                         "status": "success",
#                         "user": UserInfoSerializer(user).data
#                     }
#                 return SuccessResponse(
#                     message="Login successful",
#                     data=data
#                 )
#             else:
#                 return BadRequestResponse(
#                     message=f"{serializer.errors.get('non_field_errors', ['Invalid credentials'])[0]}",
#                     errors=serializer.errors
#                 )

#         except Exception as e:
#             return ServerErrorResponse(
#                 errors=str(e),
#             )


# # Update User View
# class UserProfileView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, JSONParser]
#     renderer_classes = [JSONRenderer]

#     @swagger_auto_schema(
#         operation_description="Retrieve authenticated user's profile",
#         responses={
#             200: create_response_serializer(
#                 data_serializer_class=UserInfoSerializer,
#                 text_message="User profile retrieved successfully"
#             )
#         }
#     )
#     def get(self, request):
#         try:
#             serializer = UserInfoSerializer(request.user)
#             return SuccessResponse(
#                 message="User profile retrieved successfully",
#                 data=serializer.data,
#             )
#         except Exception as e:
#             return ServerErrorResponse(errors=str(e))

#     @swagger_auto_schema(
#         operation_description="Update entire profile of the authenticated user",
#         request_body=UserProfileUpdateSerializer,
#         responses={
#             200: create_response_serializer(
#                 data_serializer_class=UserInfoSerializer,
#                 text_message="Profile updated successfully"
#             ),
#             400: "Bad Request"
#         }
#     )
#     def put(self, request):
#         try:
#             serializer = UserProfileUpdateSerializer(request.user, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return SuccessResponse(
#                     message="Profile updated successfully",
#                     data=UserInfoSerializer(request.user).data,
#                 )
#             return BadRequestResponse(
#                 message="Profile update failed",
#                 errors=serializer.errors
#             )
#         except Exception as e:
#             return ServerErrorResponse(errors=str(e))

#     @swagger_auto_schema(
#         operation_description="Partially update the authenticated user's profile",
#         request_body=UserProfileUpdateSerializer,
#         responses={
#             200: create_response_serializer(
#                 data_serializer_class=UserInfoSerializer,
#                 text_message="Profile updated successfully"
#             ),
#             400: "Bad Request"
#         }
#     )
#     def patch(self, request):
#         try:
#             serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return SuccessResponse(
#                     message="Profile updated successfully",
#                     data=UserInfoSerializer(request.user).data,
#                 )
#             return BadRequestResponse(
#                 message="Profile update failed",
#                 errors=serializer.errors
#             )
#         except Exception as e:
#             return ServerErrorResponse(errors=str(e))


# # Social Auth
# class GoogleSignInView(APIView):
#     parser_classes = [FormParser, JSONParser]
#     renderer_classes = [JSONRenderer]

#     @swagger_auto_schema(
#         operation_description="Sign in with Google access token",
#         request_body=GoogleSignInSerializer,
#         responses={
#             200: create_response_serializer(
#                 data_serializer_class=RegisteredUserSerializer,
#                 text_message="Google sign-in successful"
#             ),
#         },
#     )
#     def post(self, request):
#         try:
#             serializer = GoogleSignInSerializer(data=request.data)
#             if not serializer.is_valid():
#                 return BadRequestResponse(
#                     message="Invalid data",
#                     errors=serializer.errors,
#                 )

#             user_access_token = serializer.validated_data['access_token']
#             if not user_access_token:
#                 return BadRequestResponse(
#                     message="The value of access_token can't be null"
#                 )

#             # Fetch user info from Google
#             response = requests.get(
#                 'https://www.googleapis.com/oauth2/v3/userinfo',
#                 headers={'Authorization': f'Bearer {user_access_token}'},
#             )
#             if response.status_code != 200:
#                 return BadRequestResponse(
#                     message="Invalid access token or user info could not be retrieved"
#                 )

#             user_info = response.json()
#             email = user_info['email']
#             name = user_info.get('name', '')
#             google_id = user_info['sub']
#             picture_link = user_info.get('picture')

#             user, created = User.objects.get_or_create(
#                 email=email,
#                 defaults={
#                     "username": email,
#                     "full_name": name,
#                     "google_id": google_id,
#                     "is_email_confirmed": True,
#                 },
#             )

#             # If new user, assign default role + create profile
#             if created:
#                 user.set_password(User.objects.make_random_password())
#                 user.save()

#                 # Default: new Google user is a Client
#                 from apps.account.models import Client
#                 Client.objects.create(user=user)

#                 # Download Google profile picture
#                 if picture_link:
#                     pic_response = requests.get(picture_link)
#                     if pic_response.status_code == status.HTTP_200_OK:
#                         temp_file = NamedTemporaryFile(delete=True)
#                         temp_file.write(pic_response.content)
#                         user.profile_picture.save(
#                             f"{user.username}_google.png",
#                             File(temp_file),
#                             save=True,
#                         )

#             # Login and generate tokens
#             refresh = RefreshToken.for_user(user)
#             login(request, user)
#             data = {
#                 "access_token": str(refresh.access_token),
#                 "refresh_token": str(refresh),
#                 "status": "success",
#                 "user": UserInfoSerializer(user).data,
#             }

#             return (
#                 SuccessResponse201(message="Registration successful", data=data)
#                 if created
#                 else SuccessResponse(message="Login successful", data=data)
#             )

#         except Exception as e:
#             return ServerErrorResponse(errors=str(e))
