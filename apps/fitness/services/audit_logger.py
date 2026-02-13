from apps.fitness.models.program_assignment_audit import ProgramAssignmentAudit


class AssignmentAuditLogger:

    @staticmethod
    def log(
        *,
        actor,
        client,
        program,
        assignment,
        action,
        meta=None
    ):
        ProgramAssignmentAudit.objects.create(
            actor=actor,
            client=client,
            program=program,
            assignment=assignment,
            action=action,
            meta=meta or {},
        )
