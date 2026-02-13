from rest_framework import serializers
from apps.account.models import User
from apps.fitness.models.coach_client import CoachClient


class CoachClientCreateSerializer(serializers.ModelSerializer):
    client_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CoachClient
        fields = ['client_id', 'notes']

    def validate_client_id(self, value):
        request = self.context['request']

        if value == request.user.id:
            raise serializers.ValidationError("You cannot add yourself as a client.")

        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Client not found.")

        return value

    def create(self, validated_data):
        coach = self.context['request'].user
        client_id = validated_data.pop('client_id')
        client = User.objects.get(id=client_id)

        return CoachClient.objects.create(
            coach=coach,
            client=client,
            **validated_data
        )
