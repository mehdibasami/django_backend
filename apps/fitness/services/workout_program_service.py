from django.shortcuts import get_object_or_404
from apps.fitness.models.workout import WorkoutProgram, WorkoutSession, WorkoutExercise, Exercise
from config.utils.exceptions import ForbiddenException, NotFoundException


class WorkoutProgramService:

    @staticmethod
    def validate_exercises(exercises_data):
        """Ensure all exercise IDs exist"""
        for ex_data in exercises_data:
            exercise = ex_data.get('exercise')
            if not Exercise.objects.filter(id=exercise.id).exists():
                raise NotFoundException(f"Exercise with ID {exercise.id} does not exist.")

    @staticmethod
    def create_program_with_sessions(actor, data):
        sessions_data = data.pop('sessions', [])
        program = WorkoutProgram.objects.create(created_by=actor, **data)

        for session_data in sessions_data:
            exercises_data = session_data.pop('exercises', [])
            # Validate exercises
            WorkoutProgramService.validate_exercises(exercises_data)

            session = WorkoutSession.objects.create(program=program, created_by=actor, **session_data)
            for exercise_data in exercises_data:
                WorkoutExercise.objects.create(session=session, **exercise_data)

        return program

    @staticmethod
    def update_program_with_sessions(actor, program_id, data):
        program = get_object_or_404(WorkoutProgram, id=program_id)
        if program.created_by != actor:
            raise ForbiddenException("You cannot edit this program.")

        sessions_data = data.pop('sessions', None)
        for attr, value in data.items():
            setattr(program, attr, value)
        program.save()

        if sessions_data is not None:
            program.sessions.all().delete()
            for session_data in sessions_data:
                exercises_data = session_data.pop('exercises', [])
                # Validate exercises
                WorkoutProgramService.validate_exercises(exercises_data)

                session = WorkoutSession.objects.create(program=program, created_by=actor, **session_data)
                for exercise_data in exercises_data:
                    WorkoutExercise.objects.create(session=session, **exercise_data)

        return program

    @staticmethod
    def clone_program(actor, program_id):
        program = get_object_or_404(WorkoutProgram, id=program_id)

        new_program = WorkoutProgram.objects.create(
            title=f"{program.title} (Copy)",
            description=program.description,
            level=program.level,
            goal=program.goal,
            duration=program.duration,
            price=program.price,
            off_percent=program.off_percent,
            is_active=False,
            is_public=False,
            is_custom=program.is_custom,
            is_verified=False,
            video=program.video,
            location=program.location,
            equipment=program.equipment,
            created_by=actor,
        )

        for session in program.sessions.all():
            new_session = WorkoutSession.objects.create(
                program=new_program,
                title=session.title,
                notes=session.notes,
                week_number=session.week_number,
                session_type=session.session_type,
                duration=session.duration,
                intensity=session.intensity,
                is_rest_day=session.is_rest_day,
                created_by=actor,
            )

            for exercise in session.exercises.all():
                # Validate that exercise still exists
                if not Exercise.objects.filter(id=exercise.exercise.id).exists():
                    continue  # Skip missing exercises
                WorkoutExercise.objects.create(
                    session=new_session,
                    exercise=exercise.exercise,
                    sets=exercise.sets,
                    reps=exercise.reps,
                    duration=exercise.duration,
                    rest_time=exercise.rest_time,
                    tempo=exercise.tempo,
                )

        return new_program

    @staticmethod
    def delete_program(actor, program_id):
        program = get_object_or_404(WorkoutProgram, id=program_id)
        if program.created_by != actor:
            raise ForbiddenException("You cannot delete this program.")
        program.delete()
        return True

    @staticmethod
    def publish_program(actor, program_id):
        program = get_object_or_404(WorkoutProgram, id=program_id)
        if program.created_by != actor:
            raise ForbiddenException("You cannot publish this program.")
        program.is_public = True
        program.save()
        return program
