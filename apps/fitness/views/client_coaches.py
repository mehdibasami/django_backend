from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.fitness.models.coach_client import CoachClient
from config.utils.response_state import SuccessResponse


class ClientCoachListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        relations = CoachClient.objects.filter(
            client=request.user,
            is_active=True
        ).select_related('coach')

        data = [
            {
                "coach_id": r.coach.id,
                "coach_name": r.coach.full_name,
                "coach_email": r.coach.email,
                "since": r.created_at,
            }
            for r in relations
        ]

        return SuccessResponse(data=data, status=status.HTTP_200_OK)
