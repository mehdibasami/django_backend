from rest_framework import serializers
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError
from apps.account.models import User, CoachProfile
from apps.account.serializers.profile import UserInfoSerializer


# ---------------- REGISTER ----------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    is_coach = serializers.BooleanField(default=False)
    is_gym_owner = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ["email", "password", "full_name", "is_coach", "is_gym_owner"]

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        is_coach = validated_data.pop("is_coach", False)
        is_gym_owner = validated_data.pop("is_gym_owner", False)

        user = User(
            email=validated_data["email"],
            username=validated_data["email"],
            full_name=validated_data.get("full_name", ""),
            is_coach=is_coach,
            is_gym_owner=is_gym_owner,
        )
        user.set_password(validated_data["password"])
        user.save()

        if is_coach:
            CoachProfile.objects.create(user=user)

        return user


# ---------------- LOGIN ----------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(
            username=attrs.get("email"),
            password=attrs.get("password"),
        )
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")
        return user


# ---------------- GOOGLE ----------------
class GoogleSignInSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    is_coach = serializers.BooleanField(default=False)
    is_gym_owner = serializers.BooleanField(default=False)


# --------------------------------
# Registered User Serializer (Response after Register)
# --------------------------------
class RegisteredUserResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    status = serializers.CharField()
    user = UserInfoSerializer()
