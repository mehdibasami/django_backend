# apps/fitness/serializers/exercise.py

from rest_framework import serializers
from apps.fitness.models.workout import (
    Exercise,
    ExerciseImage,
    ExerciseVideo,
    ExerciseMuscleGroup,
)


class ExerciseImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseImage
        fields = ['id', 'image_file']


class ExerciseVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseVideo
        fields = ['id', 'video_file']


class ExerciseMuscleGroupSerializer(serializers.ModelSerializer):
    muscle_group_title = serializers.CharField(
        source='muscle_group.title',
        read_only=True
    )

    class Meta:
        model = ExerciseMuscleGroup
        fields = [
            'muscle_group',
            'muscle_group_title',
            'is_primary',
        ]


class ExerciseSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()
    muscle_groups = ExerciseMuscleGroupSerializer(
        source='exercise_muscle_entries',
        many=True,
        required=False
    )

    class Meta:
        model = Exercise
        fields = [
            'id',
            'name',
            'slug',
            'instructions',
            'category',
            'modalities',
            'training_system',
            'level',
            'intensity',
            'is_public',
            'is_custom',
            'is_multiple_exercise',
            'muscle_groups',
            'images',
            'videos',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def get_images(self, obj):
        return [img.image_file.url for img in obj.images.all()]

    def get_videos(self, obj):
        return [vid.video_file.url for vid in obj.videos.all()]
