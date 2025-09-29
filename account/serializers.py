from rest_framework import serializers
from account.models import Address, User, UserRole
import logging
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

logger = logging.getLogger(__name__)


# Address Serializer
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['city', 'province', 'address', 'zip_code']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=UserRole.choices())

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name', 'role')

    def validate_password(self, value):
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['email'],
            full_name=validated_data['full_name'],
            role=validated_data['role']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_email(self, value):
        """
        Custom validation to ensure that the email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled")
        return user


class UserInfoSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = [
            "password",
            "is_superuser",
            "username",
            "is_staff",
            "groups",
            "user_permissions",
        ]

    def get_role(self, obj):
        """
        Custom method to get the role of the user.
        """
        return obj.get_role_display() if obj.role else None


class RegisteredUserSerializer(serializers.Serializer):
    """
    Serializer for the Register API response.
    """
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    status = serializers.CharField()
    user = UserInfoSerializer()


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "full_name", "phone_number", "gender", "birth_date", "biography",
            "profile_picture", "address", "skills", "company_name",
            "company_website", "years_of_experience"
        ]

    def update(self, instance, validated_data):
        address_data = validated_data.pop("address", None)
        if address_data:
            if instance.address:
                for key, value in address_data.items():
                    setattr(instance.address, key, value)
                instance.address.save()
            else:
                address = Address.objects.create(**address_data)
                instance.address = address

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class GmailSerializer(serializers.Serializer):
    access_token = serializers.CharField(default="string")
