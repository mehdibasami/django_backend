from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from apps.account.models import CoachProfile
from apps.account.serializers import CoachProfileSerializer
from config.utils.response_state import (
    SuccessResponse, BadRequestResponse, ServerErrorResponse,
    NotFoundResponse, ForbiddenResponse
)
from apps.account.permissions.roles import IsCoach
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from config.utils.pagination import StandardResultsSetPagination
from apps.account.models import User


class CoachProfileView(APIView):
    """
    View to retrieve any coach profile (readable by all authenticated users)
    and allow only the coach themselves to update their profile
    """
    # GET: any authenticated user, PATCH: only coaches
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get a coach profile by user ID",
        responses={200: CoachProfileSerializer},
    )
    def get(self, request, coach_id):
        try:
            profile = CoachProfile.objects.get(user__id=coach_id)
            serializer = CoachProfileSerializer(profile)
            return SuccessResponse(
                message="Coach profile retrieved successfully",
                data=serializer.data
            )
        except CoachProfile.DoesNotExist:
            return NotFoundResponse(message="Coach profile not found.")
        except Exception as e:
            return ServerErrorResponse(message=str(e))

    @swagger_auto_schema(
        operation_description="Update the authenticated coach's profile",
        request_body=CoachProfileSerializer,
        responses={200: CoachProfileSerializer},
    )
    def patch(self, request):
        try:
            # Only allow coaches to update their own profile
            if not IsCoach().has_permission(request, self):
                return ForbiddenResponse(message="Only coaches can update their profile.")

            profile = getattr(request.user, 'coach_profile', None)
            if not profile:
                return NotFoundResponse(message="Coach profile not found.")

            serializer = CoachProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return SuccessResponse(
                    message="Coach profile updated successfully",
                    data=serializer.data
                )
            return BadRequestResponse(errors=serializer.errors)
        except Exception as e:
            return ServerErrorResponse(message=str(e))


class CoachListView(APIView):
    """
    List all coaches
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        operation_description="Retrieve a paginated list of all coaches",
        responses={200: CoachProfileSerializer(many=True)},
    )
    def get(self, request):
        try:
            queryset = User.objects.filter(is_coach=True, is_active=True).select_related('coach_profile')

            paginator = self.pagination_class()
            paginated = paginator.paginate_queryset(queryset, request, view=self)

            # Only return coach profiles
            data = []
            for user in paginated:
                if hasattr(user, 'coach_profile'):
                    serializer = CoachProfileSerializer(user.coach_profile)
                    data.append(serializer.data)

            return SuccessResponse(
                message="Coaches retrieved successfully",
                data=paginator.get_paginated_response(data).data
            )
        except Exception as e:
            return ServerErrorResponse(message=str(e))
