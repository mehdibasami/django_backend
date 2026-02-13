from django.shortcuts import get_object_or_404
from apps.fitness.models.workout import WorkoutSession, WorkoutProgram
from config.utils.exceptions import ForbiddenException


class WorkoutSessionService:

    @staticmethod
    def create_session(*, actor, data):
        program = None
        program_id = data.pop('program_id', None)

        if program_id:
            program = get_object_or_404(WorkoutProgram, id=program_id)

            if program.created_by != actor:
                raise ForbiddenException("You are not allowed to add sessions to this program.")

        return WorkoutSession.objects.create(
            program=program,
            created_by=actor,
            **data
        )

    @staticmethod
    def update_session(*, actor, session_id, data):
        session = get_object_or_404(WorkoutSession, id=session_id)

        if session.created_by != actor:
            raise ForbiddenException("You cannot edit this session.")

        for field, value in data.items():
            setattr(session, field, value)

        session.save()
        return session

    @staticmethod
    def delete_session(*, actor, session_id):
        session = get_object_or_404(WorkoutSession, id=session_id)

        if session.created_by != actor:
            raise ForbiddenException("You cannot delete this session.")

        session.delete()
        return True

    @staticmethod
    def list_sessions(*, actor, program_id=None):
        qs = WorkoutSession.objects.all()

        if program_id:
            qs = qs.filter(program_id=program_id)

        return qs.order_by('week_number', 'created_at')

    @staticmethod
    def get_session(*, actor, session_id):
        return get_object_or_404(WorkoutSession, id=session_id)
