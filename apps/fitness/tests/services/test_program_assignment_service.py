import pytest
from django.contrib.auth import get_user_model
from apps.fitness.models.program_assignment_audit import ProgramAssignmentAudit
from apps.fitness.models.workout import WorkoutProgram, ProgramAssignment
from apps.fitness.models.coach_client import CoachClient
from apps.fitness.services.program_assignment_service import ProgramAssignmentService
from config.utils.exceptions import BadRequestException, NotFoundException, ForbiddenException

User = get_user_model()


@pytest.mark.django_db
class TestProgramAssignmentService:

    @pytest.fixture
    def coach(self):
        return User.objects.create(username="coach1", email="coach1@example.com", is_coach=True, is_active=True)

    @pytest.fixture
    def client(self):
        return User.objects.create(username="client1", email="client1@example.com", is_active=True)

    @pytest.fixture
    def program(self, coach):
        return WorkoutProgram.objects.create(title="Test Program", created_by=coach, is_active=True)

    @pytest.fixture
    def coach_client_relation(self, coach, client):
        return CoachClient.objects.create(coach=coach, client=client, is_active=True)

    # Helper to get latest audit log
    def get_latest_audit(self, assignment):
        return ProgramAssignmentAudit.objects.filter(assignment=assignment).latest('created_at')

    def test_assign_program_success(self, coach, client, program, coach_client_relation):
        assignment = ProgramAssignmentService.assign_program(actor=coach, client_id=client.id, program_id=program.id)
        assert assignment.is_active is True
        assert assignment.coach == coach
        assert assignment.client == client
        assert assignment.program == program

        audit = self.get_latest_audit(assignment)
        assert audit.action.lower() == "assigned"

    def test_assign_program_already_assigned(self, coach, client, program, coach_client_relation):
        ProgramAssignment.objects.create(client=client, program=program, coach=coach, is_active=True)
        with pytest.raises(BadRequestException):
            ProgramAssignmentService.assign_program(actor=coach, client_id=client.id, program_id=program.id)

    def test_assign_program_reactivate(self, coach, client, program, coach_client_relation):
        old_assignment = ProgramAssignment.objects.create(client=client, program=program, coach=coach, is_active=False)
        assignment = ProgramAssignmentService.assign_program(actor=coach, client_id=client.id, program_id=program.id)
        assert assignment.id == old_assignment.id
        assert assignment.is_active is True

        audit = self.get_latest_audit(assignment)
        assert audit.action.lower() == "reassigned"

    def test_unassign_program_success(self, coach, client, program, coach_client_relation):
        assignment = ProgramAssignment.objects.create(client=client, program=program, coach=coach, is_active=True)
        unassigned = ProgramAssignmentService.unassign_program(actor=coach, assignment_id=assignment.id)
        assert unassigned.is_active is False

        audit = self.get_latest_audit(unassigned)
        assert audit.action.lower() == "unassigned"

    def test_unassign_program_not_found(self, coach):
        with pytest.raises(NotFoundException):
            ProgramAssignmentService.unassign_program(actor=coach, assignment_id=999)

    def test_unassign_program_forbidden(self, coach, client, program):
        other_coach = User.objects.create(username="coach2", email="coach2@example.com", is_coach=True, is_active=True)
        assignment = ProgramAssignment.objects.create(client=client, program=program, coach=other_coach, is_active=True)
        with pytest.raises(ForbiddenException):
            ProgramAssignmentService.unassign_program(actor=coach, assignment_id=assignment.id)

    def test_get_assignment_history_client_self(self, coach, client, program, coach_client_relation):
        ProgramAssignment.objects.create(client=client, program=program, coach=coach, is_active=True)
        assignments = ProgramAssignmentService.get_assignment_history(actor=client, client_id=client.id)
        assert len(assignments) == 1

    def test_get_assignment_history_coach(self, coach, client, program, coach_client_relation):
        ProgramAssignment.objects.create(client=client, program=program, coach=coach, is_active=True)
        assignments = ProgramAssignmentService.get_assignment_history(actor=coach, client_id=client.id)
        assert len(assignments) == 1

    def test_get_assignment_history_forbidden(self, client):
        other_client = User.objects.create(username="client2", is_active=True)
        with pytest.raises(ForbiddenException):
            ProgramAssignmentService.get_assignment_history(actor=client, client_id=other_client.id)
