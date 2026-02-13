# apps/fitness/services/program_assignment_service.py

from django.db import transaction
from django.utils.dateparse import parse_date
from django.db import IntegrityError

from apps.account.models import User
from apps.fitness.models.program_assignment_audit import ProgramAssignmentAudit
from apps.fitness.models.workout import ProgramAssignment, WorkoutProgram
from apps.fitness.models.coach_client import CoachClient
from apps.fitness.services.audit_logger import AssignmentAuditLogger
from apps.payments.models.coach_service import CoachServiceRequest
from apps.payments.services.coach_request_service import CoachRequestService
from config.utils.exceptions import (
    BadRequestException,
    NotFoundException,
    ForbiddenException,
)


class ProgramAssignmentService:

    @staticmethod
    @transaction.atomic
    def assign_program(*, actor, client_id, program_id, coach_request_id=None):
        """
        Assign a workout program.
        If coach_request_id is provided, it MUST be paid and valid.
        """

        # ---------------------------
        # Validate client
        # ---------------------------
        client = User.objects.filter(id=client_id, is_active=True).first()
        if not client:
            raise NotFoundException("Client not found.")

        # ---------------------------
        # Validate program
        # ---------------------------
        program = WorkoutProgram.objects.filter(id=program_id, is_active=True).first()
        if not program:
            raise NotFoundException("Workout program not found.")

        if actor.is_coach and program.created_by != actor:
            raise ForbiddenException("You can only assign your own programs.")

        # ---------------------------
        # Optional: validate paid coach request
        # ---------------------------
        coach_request = None

        if coach_request_id:
            coach_request = CoachServiceRequest.objects.select_for_update().filter(
                id=coach_request_id
            ).first()

            if not coach_request:
                raise NotFoundException("Coach service request not found.")

            if coach_request.client != client:
                raise ForbiddenException("Request does not belong to this client.")

            if coach_request.service.coach != actor:
                raise ForbiddenException("You are not assigned to this request.")

            if coach_request.status != 'paid':
                raise ForbiddenException("Service request must be paid before assignment.")

            if hasattr(coach_request, 'program_assignment'):
                raise BadRequestException("This service request has already been fulfilled.")

        # ---------------------------
        # Existing assignment check
        # ---------------------------
        assignment = ProgramAssignment.objects.filter(
            client=client,
            program=program
        ).first()

        if assignment and assignment.is_active:
            raise BadRequestException("This program is already assigned.")

        # ---------------------------
        # Create or reactivate assignment
        # ---------------------------
        if assignment:
            assignment.is_active = True
            assignment.coach = actor
            assignment.coach_service_request = coach_request
            assignment.save()
        else:
            assignment = ProgramAssignment.objects.create(
                coach=actor,
                client=client,
                program=program,
                coach_service_request=coach_request,
                is_active=True
            )
        # 🔥 AUTO-COMPLETE REQUEST
        if coach_request:
            CoachRequestService.complete_request(
                request_obj=coach_request,
                actor=actor
            )

        # ---------------------------
        # Audit log
        # ---------------------------
        AssignmentAuditLogger.log(
            actor=actor,
            client=client,
            program=program,
            assignment=assignment,
            action=ProgramAssignmentAudit.Action.ASSIGNED,
        )

        return assignment

    @staticmethod
    @transaction.atomic
    def unassign_program(*, actor, assignment_id):
        """
        Soft-unassign a workout program.
        """

        assignment = ProgramAssignment.objects.filter(
            id=assignment_id,
            is_active=True
        ).select_related("coach").first()

        if not assignment:
            raise NotFoundException("Assignment not found.")

        # ---------------------------
        # Ownership check
        # ---------------------------
        if assignment.coach and assignment.coach != actor:
            raise ForbiddenException(
                "You are not allowed to unassign this program."
            )

        assignment.is_active = False
        try:
            assignment.save(update_fields=["is_active"])
        except IntegrityError:
            raise BadRequestException(
                    "This program is already assigned to the client."
                )
        AssignmentAuditLogger.log(
            actor=actor,
            client=assignment.client,
            program=assignment.program,
            assignment=assignment,
            action=ProgramAssignmentAudit.Action.UNASSIGNED,
        )
        return assignment

    # --------------------------------
    # READ — Assignment History
    # --------------------------------
    @staticmethod
    def get_assignment_history(*, actor, client_id, filters=None):
        """
        Returns assignment history for a client
        with strict access control and filtering.
        """

        filters = filters or {}

        queryset = ProgramAssignment.objects.select_related(
            "program",
            "coach",
        ).filter(client_id=client_id)

        # ---------------------------
        # Access control
        # ---------------------------
        if actor.id == client_id:
            pass  # client can see own history

        elif actor.is_coach:
            owns_client = CoachClient.objects.filter(
                coach=actor,
                client_id=client_id,
                is_active=True
            ).exists()

            if not owns_client:
                raise ForbiddenException(
                    "You are not allowed to view this client's assignment history."
                )

            queryset = queryset.filter(coach=actor)

        elif actor.is_gym_owner or actor.is_staff:
            pass  # full access

        else:
            raise ForbiddenException("You are not allowed to access this resource.")

        # ---------------------------
        # Apply filters
        # ---------------------------
        is_active = filters.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(
                is_active=str(is_active).lower() == "true"
            )

        program_id = filters.get("program_id")
        if program_id:
            queryset = queryset.filter(program_id=program_id)

        from_date = parse_date(filters.get("from_date")) if filters.get("from_date") else None
        if from_date:
            queryset = queryset.filter(assigned_at__date__gte=from_date)

        to_date = parse_date(filters.get("to_date")) if filters.get("to_date") else None
        if to_date:
            queryset = queryset.filter(assigned_at__date__lte=to_date)

        return queryset.order_by("-assigned_at")
