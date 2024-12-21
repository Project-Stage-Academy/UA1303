from rest_framework import serializers
from .models import StartupProfile
from projects.serializers import ProjectSerializer
from rest_framework.exceptions import ValidationError


class StartupProfileSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = StartupProfile
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        if self.context['request'].method == 'POST' and StartupProfile.objects.filter(user=user).exists():
            raise ValidationError("You already have a startup profile.")
        return data