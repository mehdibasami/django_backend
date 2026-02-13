from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.fitness.models.coach_client import CoachClient
from apps.fitness.serializers.coach_client import CoachClientCreateSerializer
from apps.account.permissions.roles import IsCoach
from config.utils.response_state import SuccessResponse, NotFoundResponse


class CoachClientListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCoach]

    @swagger_auto_schema(
        operation_description="List all active clients of the authenticated coach",
        responses={200: openapi.Response(
            description="List of clients",
            examples={
                "application/json": [
                    {
                        "id": "uuid",
                        "client_id": "uuid",
                        "client_name": "John Doe",
                        "client_email": "john@example.com",
                        "notes": "Some notes",
                        "since": "2025-12-21T12:34:56Z"
                    }
                ]
            }
        )}
    )
    def get(self, request):
        relations = CoachClient.objects.filter(
            coach=request.user,
            is_active=True
        ).select_related('client')

        data = [
            {
                "id": r.id,
                "client_id": r.client.id,
                "client_name": r.client.full_name,
                "client_email": r.client.email,
                "notes": r.notes,
                "since": r.created_at,
            }
            for r in relations
        ]

        return SuccessResponse(data=data)

    @swagger_auto_schema(
        operation_description="Add a new client to the authenticated coach",
        request_body=CoachClientCreateSerializer,
        responses={
            201: openapi.Response(
                description="Client added successfully",
                examples={"application/json": {"message": "Client added successfully", "id": "uuid"}}
            ),
            400: "Validation error"
        }
    )
    def post(self, request):
        serializer = CoachClientCreateSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        relation = serializer.save()

        return SuccessResponse(
            message="Client added successfully",
            data={"id": relation.id},
            status_code=201
        )


class CoachClientDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsCoach]

    @swagger_auto_schema(
        operation_description="Soft delete a client from the authenticated coach",
        responses={
            200: openapi.Response(
                description="Client removed successfully",
                examples={"application/json": {"message": "Client removed"}}
            ),
            404: openapi.Response(
                description="Client not found or not associated with you",
                examples={"application/json": {"detail": "Client not found or not associated with you."}}
            )
        }
    )
    def delete(self, request, pk):
        relation = CoachClient.objects.filter(
            id=pk,
            coach=request.user,
            is_active=True
        ).first()

        if not relation:
            return NotFoundResponse(message="Client not found or not associated with you.")

        relation.is_active = False
        relation.save(update_fields=['is_active'])

        return SuccessResponse(message="Client removed")
