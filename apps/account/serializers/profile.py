from rest_framework import serializers
from apps.account.models import User
from .coach import CoachProfileSerializer


class UserInfoSerializer(serializers.ModelSerializer):
    coach_profile = CoachProfileSerializer(read_only=True)
    rate = serializers.FloatField(read_only=True)

    class Meta:
        model = User
        exclude = [
            "password",
            "is_superuser",
            "is_staff",
            "groups",
            "user_permissions",
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = [
            "id",
            "email",
            "username",
            "password",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
            "date_joined",
        ]
