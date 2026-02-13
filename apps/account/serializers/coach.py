from rest_framework import serializers
from apps.account.models import CoachProfile


class CoachProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachProfile
        fields = [
            "bio",
            "specialties",
            "years_of_experience",
            "price",
            "is_verified",
        ]
        read_only_fields = ["is_verified"]
