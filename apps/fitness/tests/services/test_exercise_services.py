import pytest
from django.contrib.auth import get_user_model
from apps.fitness.models.workout import Exercise

User = get_user_model()


@pytest.mark.django_db
def test_create_exercise():
    user = User.objects.create(username="user1", email="user1@example.com", is_active=True)
    exercise = Exercise.objects.create(name="Push Up", created_by=user)
    assert exercise.id is not None
