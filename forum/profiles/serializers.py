from rest_framework import serializers
from .models import StartupProfile
from projects.serializers import ProjectSerializer


class StartupProfileSerializer(serializers.ModelSerializer):
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = StartupProfile
        fields = '__all__'
        read_only_fields = ['user']